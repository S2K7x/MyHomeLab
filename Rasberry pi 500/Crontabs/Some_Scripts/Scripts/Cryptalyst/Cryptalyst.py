#!/usr/bin/env python3
"""
Market Analyst Bot - Analyse simplifiée des actualités financières
Version actions/bourses avec output clair et actionnable
"""
import asyncio
import os
import sqlite3
import feedparser
import argparse
import json
import time
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
import aiohttp
import requests
from google import genai
from google.genai import types

# === Configuration ===
parser = argparse.ArgumentParser(description="Market Analyst Bot")
parser.add_argument("--debug", action="store_true", help="Mode debug")
args = parser.parse_args()
DEBUG = args.debug

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RSS_FEEDS = [f.strip() for f in os.getenv("RSS_FEEDS", "").split(",") if f.strip()]
DB_PATH = os.getenv("DB_PATH", "market_news.db")
RSS_DELAY_SEC = int(os.getenv("RSS_DELAY_SEC", "2"))

if not DISCORD_WEBHOOK_URL or not GEMINI_API_KEY:
    raise SystemExit("❌ Variables manquantes: DISCORD_WEBHOOK_URL ou GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def log(msg):
    """Log uniquement en mode debug"""
    if DEBUG:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# === Database ===
def init_db():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS seen_news (
            guid TEXT PRIMARY KEY,
            title TEXT,
            link TEXT,
            published TEXT,
            source TEXT,
            seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Index pour performances
    c.execute("CREATE INDEX IF NOT EXISTS idx_seen_at ON seen_news(seen_at)")
    conn.commit()
    return conn

DB = init_db()

def is_seen(guid: str) -> bool:
    """Vérifie si une news a déjà été vue"""
    cur = DB.cursor()
    cur.execute("SELECT 1 FROM seen_news WHERE guid=?", (guid,))
    return cur.fetchone() is not None

def mark_seen(guid, title, link, published, source):
    """Marque une news comme vue"""
    cur = DB.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO seen_news (guid, title, link, published, source) VALUES (?, ?, ?, ?, ?)",
        (guid, title, link, published, source)
    )
    DB.commit()

# === RSS Fetching ===
def fetch_rss_feed(feed_url: str, timeout: int = 10):
    """Récupère et parse un flux RSS"""
    log(f"📡 Fetching: {feed_url}")
    try:
        r = requests.get(feed_url, timeout=timeout)
        r.raise_for_status()
        parsed = feedparser.parse(r.text)
        log(f"✓ {len(parsed.entries)} entries")
        time.sleep(RSS_DELAY_SEC)
        return parsed
    except Exception as e:
        log(f"⚠️ Error: {e}")
        return None

async def collect_new_articles():
    """Collecte toutes les nouvelles actualités non vues"""
    new_articles = []
    
    for feed_url in RSS_FEEDS:
        parsed = fetch_rss_feed(feed_url)
        if not parsed:
            continue
        
        source = parsed.feed.get("title") or urlparse(feed_url).netloc
        
        for entry in parsed.entries:
            guid = entry.get("id") or entry.get("guid") or entry.get("link")
            if not guid or is_seen(guid):
                continue
            
            title = entry.get("title", "Sans titre")
            link = entry.get("link", "")
            published = entry.get("published", "")
            
            new_articles.append({
                "guid": guid,
                "title": title,
                "link": link,
                "published": published,
                "source": source
            })
    
    log(f"📰 {len(new_articles)} nouvelles actualités")
    return new_articles

# === AI Analysis ===
async def analyze_market_sentiment(articles: list) -> str:
    """
    Analyse IA simplifiée et actionnable
    Output structuré en 4 sections claires
    """
    if not articles:
        return "Aucune actualité à analyser."
    
    # Construire le texte des articles
    articles_text = "\n\n".join([
        f"**{a['title']}** ({a['source']})\n{a['link']}"
        for a in articles
    ])
    
    prompt = f"""Tu es un analyste financier professionnel spécialisé dans les marchés actions.

Analyse les actualités suivantes et produis un rapport CONCIS et ACTIONABLE en français, structuré EXACTEMENT ainsi :

## 📊 SENTIMENT GÉNÉRAL
[En 2-3 phrases max : le ton global du marché aujourd'hui - Positif/Neutre/Négatif et pourquoi]

## 🎯 TOP 3 ACTUALITÉS CLÉS
1. [Titre concis] - Impact : [Haussier/Baissier/Neutre]
2. [Titre concis] - Impact : [Haussier/Baissier/Neutre]
3. [Titre concis] - Impact : [Haussier/Baissier/Neutre]

## 💡 RECOMMANDATIONS
• **À surveiller** : [2-3 secteurs ou tickers mentionnés dans les news]
• **Opportunités** : [1-2 opportunités concrètes si identifiées, sinon "Aucune opportunité claire"]
• **Risques** : [1-2 risques principaux à court terme]

## 🔮 PRÉVISION 48H
[En 1-2 phrases : tendance probable du marché dans les 2 prochains jours]
**Confiance** : [XX%]

---
**Règles strictes** :
- Maximum 250 mots au total
- Pas de jargon complexe
- Uniquement des faits issus des news fournies
- Focus sur les ACTIONS, pas la crypto
- Sois direct et actionnable

### Actualités à analyser :
{articles_text}
"""
    
    log("🤖 Envoi à Gemini...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,  # Plus factuel
                top_p=0.8
            )
        )
        return response.text
    except Exception as e:
        log(f"❌ Erreur Gemini: {e}")
        return f"⚠️ Erreur lors de l'analyse IA : {e}"

# === Discord ===
async def send_to_discord(session: aiohttp.ClientSession, content: str, max_len: int = 2000):
    """Envoie un message sur Discord (avec découpage si nécessaire)"""
    chunks = [content[i:i+max_len] for i in range(0, len(content), max_len)]
    
    for chunk in chunks:
        payload = {"content": chunk}
        async with session.post(DISCORD_WEBHOOK_URL, json=payload) as resp:
            if resp.status not in (200, 204):
                log(f"⚠️ Discord error {resp.status}: {await resp.text()}")
        await asyncio.sleep(1)

async def send_articles_summary(session: aiohttp.ClientSession, articles: list):
    """Envoie un résumé des articles sous forme de liste"""
    if not articles:
        return
    
    # Grouper par source
    by_source = {}
    for a in articles:
        source = a['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(a)
    
    # Construire le message
    msg = f"📰 **{len(articles)} nouvelles actualités détectées**\n\n"
    
    for source, items in list(by_source.items())[:5]:  # Max 5 sources
        msg += f"**{source}** ({len(items)})\n"
        for item in items[:3]:  # Max 3 articles par source
            msg += f"• {item['title'][:80]}...\n"
        if len(items) > 3:
            msg += f"  _... et {len(items)-3} autres_\n"
        msg += "\n"
    
    await send_to_discord(session, msg)

# === Main ===
async def main():
    """Fonction principale"""
    print(f"🚀 Market Analyst Bot démarré - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async with aiohttp.ClientSession() as session:
        # 1. Collecter les news
        articles = await collect_new_articles()
        
        if not articles:
            await send_to_discord(session, "📊 Aucune nouvelle actualité détectée.")
            print("✅ Aucune nouvelle actualité")
            return
        
        # 2. Marquer comme vues
        for a in articles:
            mark_seen(a["guid"], a["title"], a["link"], a["published"], a["source"])
        
        # 3. Envoyer le résumé des articles
        await send_articles_summary(session, articles)
        
        # 4. Analyse IA
        print(f"🤖 Analyse de {len(articles)} articles...")
        analysis = await analyze_market_sentiment(articles)
        
        # 5. Envoyer l'analyse
        header = "🎯 **ANALYSE MARCHÉ - Market Analyst**\n\n"
        await send_to_discord(session, header + analysis)
        
        print(f"✅ Analyse terminée et envoyée ({len(articles)} articles)")

if __name__ == "__main__":
    asyncio.run(main())

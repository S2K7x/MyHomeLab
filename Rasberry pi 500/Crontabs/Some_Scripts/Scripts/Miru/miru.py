#!/usr/bin/env python3

import os
import json
import sqlite3
import hashlib
import time
from datetime import datetime, timedelta
import email.utils
import random
import logging
import re

import requests
import feedparser
from dotenv import load_dotenv
import google.generativeai as genai

# --- Configuration ---
load_dotenv()
# MODIFICATION: Read a comma-separated list of webhook URLs
WEBHOOK_URLS_STR = os.environ.get('DISCORD_WEBHOOK_URLS')
DISCORD_WEBHOOK_URLS = [url.strip() for url in WEBHOOK_URLS_STR.split(',')] if WEBHOOK_URLS_STR else []
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
SOURCES_FILE = 'sources.json'
DB_FILE = 'miru.db'
DEDUPLICATION_DAYS = 7  # Rolling window for deduplication
REQUEST_TIMEOUT = 15  # Increased timeout
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2
MAX_ARTICLES_PER_MESSAGE = 5  # Discord embed limit per message
TIME_WINDOW_HOURS = 48  # Increased to capture more articles
DISCORD_MAX_CONTENT = 2000  # Discord content field limit
DISCORD_MAX_TITLE = 256  # Discord title limit
DISCORD_MAX_DESCRIPTION = 4096  # Discord description limit

# --- Logging Setup ---
logging.basicConfig(filename='miru.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
def setup_database():
    """Initializes the SQLite database and table if they don't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                hash TEXT PRIMARY KEY,
                timestamp INTEGER
            )
        ''')
        conn.commit()

def is_duplicate(article_hash):
    """Checks if an article hash exists in the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM articles WHERE hash = ?", (article_hash,))
        return cursor.fetchone() is not None

def add_article(article_hash):
    """Adds a new article hash and current timestamp to the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO articles (hash, timestamp) VALUES (?, ?)",
                       (article_hash, int(time.time())))
        conn.commit()

def prune_old_articles():
    """Removes records older than the deduplication window."""
    cutoff_timestamp = int(time.time()) - (DEDUPLICATION_DAYS * 24 * 60 * 60)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM articles WHERE timestamp < ?", (cutoff_timestamp,))
        deleted_count = cursor.rowcount
        conn.commit()
        if deleted_count > 0:
            logging.info(f"Pruned {deleted_count} old articles from the database.")

# --- Data Fetching & Parsing ---
def is_valid_url(url):
    """Validates if a URL is properly formatted."""
    return url and re.match(r'^https?://[^\s/$.?#].[^\s]*$', url)

def fetch_with_retries(url):
    """Fetches data from a URL with retries and exponential backoff."""
    session = requests.Session()
    retries = requests.adapters.Retry(
        total=RETRY_ATTEMPTS,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],  # Handle rate limits
    )
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT,
                               headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url} after {RETRY_ATTEMPTS} retries: {e}")
        return None

def parse_feed(source):
    """Parses RSS, Atom, JSON, or Hacker News feeds and returns recent articles."""
    response = fetch_with_retries(source['url'])
    if not response:
        return []
    
    articles = []
    cutoff_time = datetime.now() - timedelta(hours=TIME_WINDOW_HOURS)
    
    if source['type'] in ['rss', 'atom']:
        feed = feedparser.parse(response.text)
        for entry in feed.entries:
            pub_date = entry.get('published', entry.get('updated', 'No Date'))
            try:
                pub_date_parsed = datetime(*email.utils.parsedate(pub_date)[:6])
                if pub_date_parsed >= cutoff_time:
                    link = entry.get('link', '')
                    if not is_valid_url(link):
                        logging.warning(f"Skipping article with invalid URL: {entry.get('title')}")
                        continue
                    articles.append({
                        'title': entry.get('title', 'No Title')[:DISCORD_MAX_TITLE],
                        'link': link,
                        'pub_date': pub_date_parsed.isoformat() + 'Z',
                        'description': entry.get('description', entry.get('summary', ''))[:DISCORD_MAX_DESCRIPTION],
                        'image': entry.media_content[0].get('url') if 'media_content' in entry and entry.media_content and is_valid_url(entry.media_content[0].get('url')) else None,
                        'author': entry.get('author', '')[:DISCORD_MAX_TITLE]
                    })
            except (TypeError, ValueError) as e:
                logging.warning(f"Skipping article due to parsing error: {entry.get('title')}, Error: {e}")
                continue
    elif source['type'] == 'json':
        try:
            if not response.text.strip() or 'application/json' not in response.headers.get('Content-Type', ''):
                logging.warning(f"Non-JSON or empty response from {source['name']}")
                return []
            data = response.json()
            for report in data.get('reports', []):
                pub_date = report.get('disclosed_at', 'No Date')
                try:
                    pub_date_parsed = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    if pub_date_parsed >= cutoff_time:
                        link = report.get('url', '')
                        if not is_valid_url(link):
                            logging.warning(f"Skipping report with invalid URL: {report.get('title')}")
                            continue
                        articles.append({
                            'title': report.get('title', 'No Title')[:DISCORD_MAX_TITLE],
                            'link': link,
                            'pub_date': pub_date_parsed.isoformat() + 'Z',
                            'description': report.get('summary', '')[:DISCORD_MAX_DESCRIPTION],
                            'image': report.get('image', None) if is_valid_url(report.get('image')) else None,
                            'author': report.get('author', '')[:DISCORD_MAX_TITLE]
                        })
                except (TypeError, ValueError) as e:
                    logging.warning(f"Skipping report due to parsing error: {report.get('title')}, Error: {e}")
                    continue
        except Exception as e:
            logging.error(f"Error parsing JSON from {source['name']}: {e}")
            return []
    elif source['type'] == 'hackernews':
        try:
            ids = response.json()
            if not isinstance(ids, list):
                logging.warning(f"Unexpected response from {source['name']}")
                return []
            max_stories = 20
            for story_id in ids[:max_stories]:
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                item_resp = fetch_with_retries(item_url)
                if not item_resp:
                    continue
                try:
                    item = item_resp.json()
                    if item.get('type') != 'story':
                        continue
                    pub_time = item.get('time')
                    if pub_time is None:
                        continue
                    pub_date_parsed = datetime.utcfromtimestamp(pub_time)
                    if pub_date_parsed < cutoff_time:
                        continue
                    link = item.get('url', f'https://news.ycombinator.com/item?id={story_id}')
                    if not is_valid_url(link):
                        logging.warning(f"Skipping HN story with invalid URL: {item.get('title')}")
                        continue
                    articles.append({
                        'title': item.get('title', 'No Title')[:DISCORD_MAX_TITLE],
                        'link': link,
                        'pub_date': pub_date_parsed.isoformat() + 'Z',
                        'description': item.get('text', '')[:DISCORD_MAX_DESCRIPTION],
                        'image': None,
                        'author': item.get('by', '')[:DISCORD_MAX_TITLE]
                    })
                except Exception as e:
                    logging.warning(f"Skipping HN story due to parsing error: {item.get('title')}, Error: {e}")
                    continue
        except Exception as e:
            logging.error(f"Error parsing Hacker News feed from {source['name']}: {e}")
            return []
    
    logging.info(f"Fetched {len(articles)} recent articles from {source['name']}.")
    return articles

# --- Discord Integration ---
# MODIFICATION: This function now sends to a list of webhooks
def send_to_discord(articles=None, source_name=None, message_content=None):
    """Sends a Discord message to all configured webhooks."""
    if not DISCORD_WEBHOOK_URLS:
        logging.error("DISCORD_WEBHOOK_URLS not set. Cannot send message.")
        return

    payloads_to_send = []

    # Handle custom message (split if too long)
    if message_content:
        chunks = [message_content[i:i + DISCORD_MAX_CONTENT] for i in range(0, len(message_content), DISCORD_MAX_CONTENT)]
        for i, chunk in enumerate(chunks, 1):
            payloads_to_send.append({"content": f"{chunk} {'(continued)' if i < len(chunks) else ''}"})

    # Handle articles
    elif articles:
        for i in range(0, len(articles), MAX_ARTICLES_PER_MESSAGE):
            batch = articles[i:i + MAX_ARTICLES_PER_MESSAGE]
            embeds = []
            for article in batch:
                embed = {
                    "title": article['title'][:DISCORD_MAX_TITLE],
                    "url": article['link'],
                    "description": article.get('description', '')[:DISCORD_MAX_DESCRIPTION],
                    "color": 0x5865F2,
                    "footer": {"text": source_name},
                    "timestamp": article['pub_date']
                }
                if article.get('author'):
                    embed["author"] = {"name": article['author'][:DISCORD_MAX_TITLE]}
                if article.get('image') and is_valid_url(article['image']):
                    embed["image"] = {"url": article['image']}
                embeds.append(embed)
            
            payload = {
                "content": f"**New Articles from {source_name} (Part {i // MAX_ARTICLES_PER_MESSAGE + 1})**",
                "embeds": embeds
            }
            payloads_to_send.append(payload)

    if not payloads_to_send:
        return

    # Iterate through each configured webhook and send all generated payloads
    for webhook_url in DISCORD_WEBHOOK_URLS:
        if not webhook_url or not webhook_url.startswith('http'):
            logging.warning(f"Skipping invalid webhook URL in list: {webhook_url}")
            continue

        logging.info(f"--- Sending to webhook: {webhook_url[:35]}... ---")
        for payload in payloads_to_send:
            try:
                response = requests.post(webhook_url, json=payload, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                logging.info("Successfully sent payload to Discord.")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error sending message to {webhook_url[:35]}: {e}")
                logging.error(f"Failed payload: {json.dumps(payload, indent=2)}")
            
            time.sleep(1.5) # Avoid rate limits when sending multiple payloads

def summarize_articles_with_gemini(articles):
    """Generates a coherent summary of articles using Gemini API."""
    logging.info(f"Attempting Gemini API call for {len(articles)} articles")
    if not GEMINI_API_KEY:
        logging.warning("GEMINI_API_KEY not set. Summarization skipped.")
        return None
    genai.configure(api_key=GEMINI_API_KEY)
    prompt = "Provide a brief overview of the following news articles, highlighting key points or common themes (max 1500 characters):\n"
    for article in articles:
        prompt += f"- {article['title']} ({article['link']})\n"
    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Updated model name
        response = model.generate_content(prompt)
        summary = response.text.strip()[:1500]
        logging.info("Gemini API call successful")
        return summary
    except Exception as e:
        logging.error(f"Error using Gemini API: {e}")
        return None

# --- Main Logic ---
def main():
    """Runs the news aggregation and posting process."""
    logging.info("--- Projet Miru starting run ---")
    setup_database()

    # MODIFICATION: Check for the plural environment variable
    if not DISCORD_WEBHOOK_URLS:
        logging.error("DISCORD_WEBHOOK_URLS not set in environment. Exiting.")
        return
    if not GEMINI_API_KEY:
        logging.warning("GEMINI_API_KEY not set. Summarization will be skipped.")

    try:
        with open(SOURCES_FILE, 'r') as f:
            sources = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading {SOURCES_FILE}: {e}")
        return

    new_articles_count = 0
    all_new_articles = []
    checked_sources = 0

    for source in sources:
        logging.info(f"Fetching from {source['name']}...")
        if not is_valid_url(source['url']):
            logging.error(f"Invalid URL in sources.json: {source['url']}")
            continue
        articles = parse_feed(source)
        checked_sources += 1
        
        if not articles:
            logging.info(f"No recent articles found for {source['name']}.")
            continue

        new_articles = []
        for article in reversed(articles):
            article_hash = hashlib.sha256(article['link'].encode('utf-8')).hexdigest()
            if not is_duplicate(article_hash):
                logging.info(f"  -> New article found: {article['title']}")
                new_articles.append(article)
                add_article(article_hash)
                new_articles_count += 1
        if len(new_articles) > 20:
            logging.info(f"Too many new articles for {source['name']}, sending only the first 20.")
            new_articles = new_articles[:20]
        if new_articles:
            send_to_discord(new_articles, source['name'])
            all_new_articles.extend(new_articles)
            time.sleep(5)  # Increased delay to avoid rate limits
    
    logging.info(f"Found and processed {new_articles_count} new articles from {checked_sources} sources.")
    prune_old_articles()

    if new_articles_count == 0:
        working_messages = [
            f"Miru is awake and monitoring! No new articles from {checked_sources} sources.",
            f"All quiet on the news front, but Miru checked {checked_sources} sources!",
            f"Chugging along! No new articles, but everything's good after checking {checked_sources} sources.",
            f"Still here, still working. Nothing new from {checked_sources} sources!",
            f"Miru checked all {checked_sources} sources; no fresh articles this run.",
            f"Just a ping to say Miru is active after scanning {checked_sources} sources!",
            f"Miru scanned the horizon—no news today across {checked_sources} sources!",
            f"The cyber seas are calm. Miru stands watch over {checked_sources} sources.",
            f"No new stories, but Miru is sharpening its senses across {checked_sources} sources!",
            f"Miru did a full sweep of {checked_sources} sources—nothing slipped by!",
            f"Silence is golden. Miru is on guard after checking {checked_sources} sources.",
            f"Miru's circuits are humming, but the feeds are quiet across {checked_sources} sources.",
            f"No alerts, no worries. Miru is on duty for {checked_sources} sources!",
            f"Miru is sipping virtual coffee, waiting for headlines from {checked_sources} sources.",
            f"All systems green. Miru is ready after scanning {checked_sources} sources!",
            f"Miru's radar is clear. Awaiting the next big thing from {checked_sources} sources!"
        ]
        random_message = random.choice(working_messages)
        send_to_discord(message_content=random_message) # Simplified call
    elif all_new_articles:
        summary = summarize_articles_with_gemini(all_new_articles)
        if summary:
            send_to_discord(message_content=f"**Miru Summary:**\n{summary}") # Simplified call

    logging.info("--- Run finished ---")

if __name__ == '__main__':
    main()

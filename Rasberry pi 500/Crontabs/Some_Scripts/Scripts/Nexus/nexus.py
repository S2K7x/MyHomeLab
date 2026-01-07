import os
import random
import time
import sys
from datetime import datetime
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration and validation ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URLS_STR = os.getenv("DISCORD_WEBHOOK_URLS")
DISCORD_WEBHOOK_URLS = [url.strip() for url in WEBHOOK_URLS_STR.split(',')] if WEBHOOK_URLS_STR else []

# Files for stats and caching
STATS_FILE = "interview_stats.json"
CACHE_FILE = "interview_cache.json"

# Categories, difficulties, and flair
CATEGORIES = ["cybersecurity", "IT", "coding", "bug bounty", "Osint"]
DIFFICULTIES = ["Junior", "Mid-level", "Senior", "Expert"]
EMOJIS = ["💼", "🎤", "💡", "🔍", "🧠", "🎯", "💻", "🔐", "🕵️", "🚀"]
WITTY_REMARKS = [
    "Time to test your knowledge!",
    "Are you ready for this challenge?",
    "Let's see what you've got!",
    "Put your skills to the test!",
    "Think you can handle this one?",
    "Time to shine in the interview!"
]

# Initialize Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

def load_stats():
    """Loads total questions and achievements from a JSON file."""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                data = json.load(f)
                return {
                    "total_questions": data.get("total_questions", 0),
                    "achievements": data.get("achievements", [])
                }
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[{datetime.now()}] ⚠️ Could not read stats file ({e}). Starting fresh.")
            return {"total_questions": 0, "achievements": []}
    return {"total_questions": 0, "achievements": []}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[{datetime.now()}] ⚠️ Could not read cache file ({e}). Starting with an empty cache.")
            return {"questions": [], "tips": []}
    return {"questions": [], "tips": []}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def call_api_with_retries(prompt, max_retries=3):
    if not model:
        print(f"[{datetime.now()}] 🚨 Gemini API key not configured. Cannot make API call.")
        return None
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[{datetime.now()}] 🚨 API call failed (attempt {attempt + 1}/{max_retries}): {e}.")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

def generate_tip():
    """Generate an interview tip instead of a fact."""
    prompt = """
    Generate a short, practical interview tip for cybersecurity or tech positions.
    It should be actionable advice that helps someone prepare for interviews.
    Also, provide a link to a relevant resource or article.
    Format it like this:
    Tip: [Your tip here]
    Link: https://example.com/resource
    """
    cache = load_cache()
    response = call_api_with_retries(prompt)
    
    if response and 'Tip:' in response and 'Link:' in response:
        lines = response.split('\n')
        tip = lines[0].replace('Tip: ', '').strip()
        link = lines[1].replace('Link: ', '').strip()
        cache["tips"].append({"tip": tip, "link": link})
        if len(cache["tips"]) > 20:
            cache["tips"].pop(0)
        save_cache(cache)
        return tip, link
    else:
        print(f"[{datetime.now()}] ⚠️ API failed to generate a tip. Using a cached tip as a fallback.")
        if cache["tips"]:
            cached_tip = random.choice(cache["tips"])
            return cached_tip["tip"], cached_tip["link"]
        return "Always prepare specific examples that demonstrate your problem-solving skills.", "https://www.indeed.com/career-advice/interviewing"

def check_achievements(total, achievements):
    new_achievements = []
    if total >= 25 and "25 Questions Answered!" not in achievements:
        new_achievements.append("🏆 25 Questions Answered!")
    if total >= 50 and "Interview Pro" not in achievements:
        new_achievements.append("🔥 Interview Pro!")
    if total >= 100 and "Question Master" not in achievements:
        new_achievements.append("🌟 Question Master!")
    return new_achievements

def generate_interview_question():
    category = random.choice(CATEGORIES)
    difficulty = random.choice(DIFFICULTIES)
    emoji = random.choice(EMOJIS)
    remark = random.choice(WITTY_REMARKS)
    
    prompt = f"""
    Generate a realistic interview question for a {difficulty} level {category} position.
    The question should be something commonly asked in tech interviews.
    Include the question and some guidance on what interviewers are looking for.
    Format it like this:
    **Question:** [The interview question]
    **What they're looking for:** [Brief guidance on how to approach the answer]
    """
    
    cache = load_cache()
    response = call_api_with_retries(prompt)
    
    if response and '**Question:**' in response:
        content = f"**{emoji} {difficulty} Level {category.upper()} Interview Question**\n\n{remark}\n\n{response}"
        cache["questions"].append(content)
        if len(cache["questions"]) > 20:
            cache["questions"].pop(0)
        save_cache(cache)
    else:
        print(f"[{datetime.now()}] ⚠️ API failed to generate a question. Using a cached question as a fallback.")
        if cache["questions"]:
            content = random.choice(cache["questions"])
        else:
            content = "No cached questions available. The bot might be having trouble connecting to the API."
    
    return {
        "title": "🎤 New Interview Question Ready!",
        "content": content,
    }

def send_to_discord(embed_data):
    """Sends the embed to all configured Discord webhooks."""
    payload = {
        "username": "Nexus",
        "embeds": [embed_data]
    }
    
    for url in DISCORD_WEBHOOK_URLS:
        try:
            print(f"[{datetime.now()}] 🚀 Sending question to webhook: {url[:35]}...")
            response = requests.post(url, json=payload, timeout=10)
            if 200 <= response.status_code < 300:
                print(f"[{datetime.now()}] ✅ Question sent successfully to {url[:35]}.")
            else:
                print(f"[{datetime.now()}] ❌ Failed to send to {url[:35]}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[{datetime.now()}] 🚨 Network error sending to Discord ({url[:35]}): {e}")
        time.sleep(1.5)  # Avoid rate-limiting

def main():
    # Robust startup checks
    if not GEMINI_API_KEY:
        print(f"[{datetime.now()}] ❌ FATAL: GEMINI_API_KEY environment variable not set. Exiting.")
        sys.exit(1)
    if not DISCORD_WEBHOOK_URLS:
        print(f"[{datetime.now()}] ❌ FATAL: DISCORD_WEBHOOK_URLS environment variable not set or empty. Exiting.")
        sys.exit(1)
    
    print(f"[{datetime.now()}] 🔄 Preparing a new interview question...")
    
    stats = load_stats()
    total = stats["total_questions"]
    achievements = stats["achievements"]
    
    question = generate_interview_question()
    tip, link = generate_tip()
    
    # Create embed
    embed = {
        "title": question["title"],
        "description": question["content"],
        "color": 3447003,  # Blue color for interviews
        "footer": {"text": f"💡 Interview Tip: {tip}"},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add achievements if any are newly earned
    new_achievements = check_achievements(total, achievements)
    if new_achievements:
        embed["fields"] = [{
            "name": "🏆 New Achievements!",
            "value": "\n".join(new_achievements),
            "inline": False
        }]
    
    send_to_discord(embed)
    
    # Update stats
    stats["total_questions"] += 1
    stats["achievements"].extend(new_achievements)
    save_stats(stats)
    
    print(f"[{datetime.now()}] ✅ Interview question delivered! Total questions asked: {stats['total_questions']}")

if __name__ == "__main__":
    main()

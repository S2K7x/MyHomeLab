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

# --- MODIFICATION: Configuration and validation ---
# Centralized configuration with checks for robustness.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URLS_STR = os.getenv("DISCORD_WEBHOOK_URLS")
DISCORD_WEBHOOK_URLS = [url.strip() for url in WEBHOOK_URLS_STR.split(',')] if WEBHOOK_URLS_STR else []

# Files for stats and caching
STATS_FILE = "exercise_stats.json"
CACHE_FILE = "exercise_cache.json"

# Categories, difficulties, and flair
CATEGORIES = ["cybersecurity", "IT", "coding", "bug bounty", "Osint"]
DIFFICULTIES = ["Beginner", "Intermediate", "Advanced", "Impossible"]
EMOJIS = ["🎯", "🔥", "💻", "🔐", "🕵️", "🚀", "🧠", "💥", "⚡", "🛡️", "🧨"]
WITTY_REMARKS = [
    "Get ready to flex your cybersecurity muscles!",
    "Time to level up your coding skills!",
    "Prepare to dive into the world of IT!",
    "Let’s hunt some bugs together!",
    "Sharpen your tech skills with this challenge!",
    "Ready to become a cybersecurity ninja?"
]

# Initialize Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# --- MODIFICATION: Stats functions no longer track streaks ---
def load_stats():
    """Loads total exercises and achievements from a JSON file."""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                data = json.load(f)
                # Ensure keys exist for backwards compatibility
                return {
                    "total_exercises": data.get("total_exercises", 0),
                    "achievements": data.get("achievements", [])
                }
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[{datetime.now()}] ⚠️  Could not read stats file ({e}). Starting fresh.")
            return {"total_exercises": 0, "achievements": []}
    return {"total_exercises": 0, "achievements": []}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

# --- MODIFICATION: Improved exception handling for robustness ---
def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[{datetime.now()}] ⚠️  Could not read cache file ({e}). Starting with an empty cache.")
            return {"exercises": [], "facts": []}
    return {"exercises": [], "facts": []}

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

def generate_fact():
    prompt = """
    Generate a short, fun, and educational cybersecurity or tech-related fact.
    It should be witty, interesting, and not too long (1–2 sentences).
    Also, provide a link to a relevant resource or article.
    Format it like this:
    Fact: [Your fact here]
    Link: https://www.merriam-webster.com/dictionary/resource
    """
    cache = load_cache()
    response = call_api_with_retries(prompt)
    if response and 'Fact:' in response and 'Link:' in response:
        lines = response.split('\n')
        fact = lines[0].replace('Fact: ', '').strip()
        link = lines[1].replace('Link: ', '').strip()
        cache["facts"].append({"fact": fact, "link": link})
        if len(cache["facts"]) > 20: # Increased cache size
            cache["facts"].pop(0)
        save_cache(cache)
        return fact, link
    else:
        # --- MODIFICATION: Clearer logging on fallback ---
        print(f"[{datetime.now()}] ⚠️  API failed to generate a fact. Using a cached fact as a fallback.")
        if cache["facts"]:
            cached_fact = random.choice(cache["facts"])
            return cached_fact["fact"], cached_fact["link"]
        return "The term 'debugging' comes from Grace Hopper removing a real moth from a computer.", "https://en.wikipedia.org/wiki/Grace_Hopper"

# --- MODIFICATION: Streak logic removed ---
def check_achievements(total, achievements):
    new_achievements = []
    if total >= 50 and "50 Exercises Completed!" not in achievements:
        new_achievements.append("🏆 50 Exercises Completed!")
    if total >= 100 and "Hacker Master" not in achievements:
        new_achievements.append("🔥 Hacker Master!")
    if total >= 250 and "Forge Legend" not in achievements:
        new_achievements.append("🌟 Forge Legend!")
    return new_achievements

def generate_exercise():
    category = random.choice(CATEGORIES)
    difficulty = random.choice(DIFFICULTIES)
    emoji = random.choice(EMOJIS)
    remark = random.choice(WITTY_REMARKS)

    prompt = f"""
    Generate a short, practical exercise in {category} at {difficulty} level.
    The exercise should be engaging and challenging.
    Include a clear task description and an optional hint.
    Format it like this:
    **Task:** [Describe what user must do]
    **Hint:** [Optional hint]
    """
    cache = load_cache()
    response = call_api_with_retries(prompt)
    if response and '**Task:**' in response:
        content = f"**{emoji} {difficulty} Level {category.upper()} Exercise**\n\n{response}"
        cache["exercises"].append(content)
        if len(cache["exercises"]) > 20: # Increased cache size
            cache["exercises"].pop(0)
        save_cache(cache)
    else:
        # --- MODIFICATION: Clearer logging on fallback ---
        print(f"[{datetime.now()}] ⚠️  API failed to generate an exercise. Using a cached exercise as a fallback.")
        if cache["exercises"]:
            content = random.choice(cache["exercises"])
        else:
            content = "No cached exercises available. The bot might be having trouble connecting to the API."
    return {
        "title": f"A New Challenge Has Been Forged!",
        "content": content,
    }

def send_to_discord(embed_data):
    """Sends the embed to all configured Discord webhooks."""
    payload = {
        "username": "Forge",
        "embeds": [embed_data]
    }
    for url in DISCORD_WEBHOOK_URLS:
        try:
            print(f"[{datetime.now()}] 🚀 Sending exercise to webhook: {url[:35]}...")
            response = requests.post(url, json=payload, timeout=10)
            if 200 <= response.status_code < 300:
                print(f"[{datetime.now()}] ✅ Exercise sent successfully to {url[:35]}.")
            else:
                print(f"[{datetime.now()}] ❌ Failed to send to {url[:35]}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[{datetime.now()}] 🚨 Network error sending to Discord ({url[:35]}): {e}")
        time.sleep(1.5) # Avoid rate-limiting

def main():
    # --- MODIFICATION: Robust startup checks ---
    if not GEMINI_API_KEY:
        print(f"[{datetime.now()}] ❌ FATAL: GEMINI_API_KEY environment variable not set. Exiting.")
        sys.exit(1)
    if not DISCORD_WEBHOOK_URLS:
        print(f"[{datetime.now()}] ❌ FATAL: DISCORD_WEBHOOK_URLS environment variable not set or empty. Exiting.")
        sys.exit(1)

    print(f"[{datetime.now()}] 🔄 Forge is creating a new challenge...")

    stats = load_stats()
    total = stats["total_exercises"]
    achievements = stats["achievements"]

    exercise = generate_exercise()
    fact, link = generate_fact()

    # --- MODIFICATION: Embed is now a simple dictionary, no discord.py needed ---
    embed = {
        "title": exercise["title"],
        "description": exercise["content"],
        "color": 5793266,  # Blurple color
        "footer": { "text": f"💡 Did you know? {fact}" },
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
    stats["total_exercises"] += 1
    stats["achievements"].extend(new_achievements)
    save_stats(stats)

    print(f"[{datetime.now()}] ✅ Challenge delivered! Total exercises forged: {stats['total_exercises']}")

if __name__ == "__main__":
    main()

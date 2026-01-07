#!/usr/bin/env python3
import os
import random
import requests
import time
from datetime import datetime
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configuration
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
if not WEBHOOK_URL:
    raise RuntimeError("Define DISCORD_WEBHOOK_URL in your environment or .env file")

ENABLE_NSFW = os.getenv('ENABLE_NSFW', 'false').lower() == 'true'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Files for persistence
WEIGHTS_FILE = "weights.json"
CACHE_FILE = "cache.json"

# --- Utility Functions ---

def load_weights():
    """Loads source weights from a JSON file or initializes from SOURCES."""
    try:
        with open(WEIGHTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {s["func"]: s["weight"] for s in SOURCES}

def save_weights(weights):
    """Saves current weights to a JSON file."""
    try:
        with open(WEIGHTS_FILE, "w") as f:
            json.dump(weights, f)
    except Exception as e:
        print(f"Error saving weights: {e}")

def load_cache():
    """Loads cached API responses from a JSON file or initializes empty."""
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {s["func"]: [] for s in SOURCES if "nsfw" not in s["func"].lower()}

def save_cache(cache):
    """Saves current cache to a JSON file."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

# --- Fetch Functions for SFW Content ---

def fetch_random_dog():
    """Fetches a random dog image with caching."""
    try:
        res = requests.get("https://random.dog/woof.json", timeout=10).json()
        data = {"title": "Random Dog", "image": res["url"], "source": "Random Dog API", "source_url": "https://random.dog"}
        cache["fetch_random_dog"].append(data)
        if len(cache["fetch_random_dog"]) > 5:
            cache["fetch_random_dog"].pop(0)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random dog: {e}")
        if cache.get("fetch_random_dog"):
            return random.choice(cache["fetch_random_dog"])
        return None

def fetch_random_cat():
    """Fetches a random cat image with caching."""
    try:
        res = requests.get("https://api.thecatapi.com/v1/images/search", timeout=10).json()
        if res and isinstance(res, list) and "url" in res[0]:
            data = {"title": "Random Cat", "image": res[0]["url"], "source": "The Cat API", "source_url": "https://thecatapi.com"}
            cache["fetch_random_cat"].append(data)
            if len(cache["fetch_random_cat"]) > 5:
                cache["fetch_random_cat"].pop(0)
            return data
        print("Unexpected response from The Cat API:", res)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random cat: {e}")
        if cache.get("fetch_random_cat"):
            return random.choice(cache["fetch_random_cat"])
        return None

def fetch_random_fox():
    """Fetches a random fox image with caching."""
    try:
        res = requests.get("https://randomfox.ca/floof/", timeout=10).json()
        data = {"title": "Random Fox", "image": res["image"], "source": "Random Fox API", "source_url": "https://randomfox.ca"}
        cache["fetch_random_fox"].append(data)
        if len(cache["fetch_random_fox"]) > 5:
            cache["fetch_random_fox"].pop(0)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random fox: {e}")
        if cache.get("fetch_random_fox"):
            return random.choice(cache["fetch_random_fox"])
        return None

def fetch_random_xkcd():
    """Fetches a random XKCD comic with caching."""
    try:
        latest = requests.get("https://xkcd.com/info.0.json", timeout=10).json()["num"]
        num = random.randint(1, latest)
        info = requests.get(f"https://xkcd.com/{num}/info.0.json", timeout=10).json()
        data = {"title": info['title'], "image": info['img'], "url": f"https://xkcd.com/{num}", "source": "XKCD", "source_url": "https://xkcd.com"}
        cache["fetch_random_xkcd"].append(data)
        if len(cache["fetch_random_xkcd"]) > 5:
            cache["fetch_random_xkcd"].pop(0)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random XKCD: {e}")
        if cache.get("fetch_random_xkcd"):
            return random.choice(cache["fetch_random_xkcd"])
        return None

def fetch_random_inaturalist():
    """Fetches a random iNaturalist observation with caching."""
    try:
        res = requests.get("https://api.inaturalist.org/v1/observations?per_page=100&order_by=random&photos=true", timeout=10).json()
        if res["results"]:
            observation = random.choice(res["results"])
            title = observation.get("species_guess", "Unknown Species")
            image = observation.get("photos", [{}])[0].get("url")
            url = observation.get("uri")
            data = {"title": f"iNaturalist: {title}", "image": image, "url": url, "source": "iNaturalist", "source_url": "https://www.inaturalist.org"}
            cache["fetch_random_inaturalist"].append(data)
            if len(cache["fetch_random_inaturalist"]) > 5:
                cache["fetch_random_inaturalist"].pop(0)
            return data
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random iNaturalist: {e}")
        if cache.get("fetch_random_inaturalist"):
            return random.choice(cache["fetch_random_inaturalist"])
        return None

def fetch_random_fact():
    """Fetches a random fact with caching."""
    try:
        res = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=10).json()
        data = {"title": "Random Fact", "description": res["text"], "source": "Useless Facts", "source_url": "https://uselessfacts.jsph.pl"}
        cache["fetch_random_fact"].append(data)
        if len(cache["fetch_random_fact"]) > 5:
            cache["fetch_random_fact"].pop(0)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random fact: {e}")
        if cache.get("fetch_random_fact"):
            return random.choice(cache["fetch_random_fact"])
        return None

def fetch_random_wikipedia():
    """Fetches a random Wikipedia summary with caching."""
    try:
        res = requests.get("https://en.wikipedia.org/api/rest_v1/page/random/summary", timeout=10).json()
        data = {"title": res['title'], "description": res['extract'][:500] + "...", "url": res['content_urls']['desktop']['page'], "source": "Wikipedia", "source_url": "https://wikipedia.org"}
        cache["fetch_random_wikipedia"].append(data)
        if len(cache["fetch_random_wikipedia"]) > 5:
            cache["fetch_random_wikipedia"].pop(0)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random Wikipedia: {e}")
        if cache.get("fetch_random_wikipedia"):
            return random.choice(cache["fetch_random_wikipedia"])
        return None

def fetch_random_inspirobot():
    """Fetches a random Inspirobot image with caching."""
    try:
        url = requests.get("https://inspirobot.me/api?generate=true", timeout=10).text
        data = {"title": "Inspirobot Wisdom", "image": url, "source": "Inspirobot", "source_url": "https://inspirobot.me"}
        cache["fetch_random_inspirobot"].append(data)
        if len(cache["fetch_random_inspirobot"]) > 5:
            cache["fetch_random_inspirobot"].pop(0)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random Inspirobot: {e}")
        if cache.get("fetch_random_inspirobot"):
            return random.choice(cache["fetch_random_inspirobot"])
        return None

def fetch_random_pokemon():
    """Fetches a random Pokémon with caching."""
    try:
        poke_id = random.randint(1, 898)
        res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{poke_id}", timeout=10).json()
        data = {"title": f"Pokémon: {res['name'].capitalize()}", "image": res['sprites']['front_default'], "source": "PokéAPI", "source_url": "https://pokeapi.co"}
        cache["fetch_random_pokemon"].append(data)
        if len(cache["fetch_random_pokemon"]) > 5:
            cache["fetch_random_pokemon"].pop(0)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random Pokémon: {e}")
        if cache.get("fetch_random_pokemon"):
            return random.choice(cache["fetch_random_pokemon"])
        return None

def fetch_random_quote():
    """Fetches a random quote with caching."""
    try:
        res = requests.get("https://zenquotes.io/api/random", timeout=10).json()
        if res and isinstance(res, list) and "q" in res[0] and "a" in res[0]:
            quote = res[0]["q"]
            author = res[0]["a"]
            data = {"title": "Random Quote", "description": f'"{quote}" - {author}', "source": "ZenQuotes API", "source_url": "https://zenquotes.io"}
            cache["fetch_random_quote"].append(data)
            if len(cache["fetch_random_quote"]) > 5:
                cache["fetch_random_quote"].pop(0)
            return data
        print("Unexpected response from ZenQuotes:", res)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random quote: {e}")
        if cache.get("fetch_random_quote"):
            return random.choice(cache["fetch_random_quote"])
        return None

def fetch_random_joke():
    """Fetches a random joke with caching."""
    try:
        res = requests.get("https://v2.jokeapi.dev/joke/Any?type=single", timeout=10).json()
        joke_text = res["joke"] if res.get("type") == "single" else f"{res['setup']}\n{res['delivery']}"
        data = {"title": "Random Joke", "description": joke_text, "source": "JokeAPI", "source_url": "https://jokeapi.dev"}
        cache["fetch_random_joke"].append(data)
        if len(cache["fetch_random_joke"]) > 5:
            cache["fetch_random_joke"].pop(0)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random joke: {e}")
        if cache.get("fetch_random_joke"):
            return random.choice(cache["fetch_random_joke"])
        return None

def fetch_random_user():
    """Fetches a random user with caching."""
    try:
        res = requests.get("https://randomuser.me/api/", timeout=10).json()
        user = res["results"][0]
        name = f"{user['name']['first']} {user['name']['last']}"
        email = user['email']
        image = user['picture']['large']
        data = {"title": f"Random User: {name}", "description": f"Email: {email}", "image": image, "source": "RandomUser API", "source_url": "https://randomuser.me"}
        cache["fetch_random_user"].append(data)
        if len(cache["fetch_random_user"]) > 5:
            cache["fetch_random_user"].pop(0)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random user: {e}")
        if cache.get("fetch_random_user"):
            return random.choice(cache["fetch_random_user"])
        return None

def fetch_random_meme():
    """Fetches a random meme with caching."""
    try:
        res = requests.get("https://meme-api.com/gimme", timeout=10).json()
        data = {"title": res["title"], "image": res["url"], "source": "Meme API", "source_url": "https://meme-api.com"}
        cache["fetch_random_meme"].append(data)
        if len(cache["fetch_random_meme"]) > 5:
            cache["fetch_random_meme"].pop(0)
        return data
    except Exception as e:
        print(f"Error fetching random meme: {e}")
        if cache.get("fetch_random_meme"):
            return random.choice(cache["fetch_random_meme"])
        return None

def fetch_random_trivia():
    """Fetches a random trivia question with caching."""
    try:
        res = requests.get("https://opentdb.com/api.php?amount=1", timeout=10).json()
        question = res["results"][0]["question"]
        answer = res["results"][0]["correct_answer"]
        data = {"title": "Random Trivia", "description": f"Q: {question}\nA: {answer}", "source": "Open Trivia DB", "source_url": "https://opentdb.com"}
        cache["fetch_random_trivia"].append(data)
        if len(cache["fetch_random_trivia"]) > 5:
            cache["fetch_random_trivia"].pop(0)
        return data
    except Exception as e:
        print(f"Error fetching random trivia: {e}")
        if cache.get("fetch_random_trivia"):
            return random.choice(cache["fetch_random_trivia"])
        return None

# --- Fetch Functions for NSFW Content with Retries ---

def fetch_nsfw_waifupics(max_retries=3):
    """Fetches an NSFW waifu image with retries, no caching."""
    for attempt in range(max_retries):
        try:
            res = requests.get("https://api.waifu.pics/nsfw/waifu", timeout=10).json()
            if "url" in res and res["url"]:
                print(f"Success fetching waifu.pics (attempt {attempt+1}): {res['url']}")
                return {"title": "NSFW Waifu (waifu.pics)", "image": res["url"], "source": "waifu.pics", "source_url": "https://waifu.pics"}
            print(f"Invalid response from waifu.pics (attempt {attempt+1}): {res}")
        except Exception as e:
            print(f"Error fetching from waifu.pics (attempt {attempt+1}): {e}")
        time.sleep(1)
    print("All attempts for waifu.pics failed.")
    return None

def fetch_nsfw_nekosapi(max_retries=3):
    """Fetches an NSFW neko image with retries, no caching."""
    for attempt in range(max_retries):
        try:
            res = requests.get("https://nekosapi.com/api/v1/images?category=lewd", timeout=10).json()
            if res.get("items") and res["items"][0].get("url"):
                print(f"Success fetching nekosapi.com (attempt {attempt+1}): {res['items'][0]['url']}")
                return {"title": "NSFW Neko (nekosapi.com)", "image": res["items"][0]["url"], "source": "nekosapi.com", "source_url": "https://nekosapi.com"}
            print(f"Invalid response from nekosapi.com (attempt {attempt+1}): {res}")
        except Exception as e:
            print(f"Error fetching from nekosapi.com (attempt {attempt+1}): {e}")
        time.sleep(1)
    print("All attempts for nekosapi.com failed.")
    return None

def fetch_nsfw_waifuim(max_retries=3):
    """Fetches an NSFW waifu image with retries, no caching."""
    for attempt in range(max_retries):
        try:
            res = requests.get("https://api.waifu.im/search?is_nsfw=true", timeout=10).json()
            if res.get("images") and res["images"][0].get("url"):
                print(f"Success fetching waifu.im (attempt {attempt+1}): {res['images'][0]['url']}")
                return {"title": "NSFW Waifu (waifu.im)", "image": res["images"][0]["url"], "source": "waifu.im", "source_url": "https://waifu.im"}
            print(f"Invalid response from waifu.im (attempt {attempt+1}): {res}")
        except Exception as e:
            print(f"Error fetching from waifu.im (attempt {attempt+1}): {e}")
        time.sleep(1)
    print("All attempts for waifu.im failed.")
    return None

def fetch_nsfw_waifuim_tagged(max_retries=3):
    """Fetches a tagged NSFW waifu image with retries, no caching."""
    tags = ['waifu', 'maid', 'hentai', 'ecchi']  # Simplified tag list
    for tag in tags:
        for attempt in range(max_retries):
            try:
                url = 'https://api.waifu.im/search'
                params = {'included_tags': [tag], 'is_nsfw': 'true', 'height': '>=1000'}
                res = requests.get(url, params=params, timeout=10).json()
                if res.get("images") and res["images"][0].get("url"):
                    print(f"Success fetching waifu.im tagged (tag: {tag}, attempt {attempt+1}): {res['images'][0]['url']}")
                    return {"title": f"NSFW Waifu (waifu.im, {tag})", "image": res["images"][0]["url"], "source": "waifu.im", "source_url": "https://waifu.im"}
                print(f"Invalid response from waifu.im tagged (tag: {tag}, attempt {attempt+1}): {res}")
            except Exception as e:
                print(f"Error fetching from waifu.im tagged (tag: {tag}, attempt {attempt+1}): {e}")
            time.sleep(1)
    print("All attempts for waifu.im tagged failed.")
    return None

def fetch_nsfw_nekos_best(max_retries=3):
    """Fetches an NSFW neko image from nekos.best with retries, no caching."""
    for attempt in range(max_retries):
        try:
            res = requests.get("https://nekos.best/api/v2/neko?type=nsfw", timeout=10).json()
            if res.get("results") and res["results"][0].get("url"):
                print(f"Success fetching nekos.best (attempt {attempt+1}): {res['results'][0]['url']}")
                return {"title": "NSFW Neko (nekos.best)", "image": res["results"][0]["url"], "source": "nekos.best", "source_url": "https://nekos.best"}
            print(f"Invalid response from nekos.best (attempt {attempt+1}): {res}")
        except Exception as e:
            print(f"Error fetching from nekos.best (attempt {attempt+1}): {e}")
        time.sleep(1)
    print("All attempts for nekos.best failed.")
    return None

def fetch_random_nsfw_anime():
    """Tries multiple NSFW anime APIs with retries, falls back to static content."""
    for func in [fetch_nsfw_waifupics, fetch_nsfw_nekosapi, fetch_nsfw_waifuim, fetch_nsfw_waifuim_tagged, fetch_nsfw_nekos_best]:
        data = func(max_retries=3)
        if data:
            return data
    print("All NSFW anime APIs failed, using static fallback.")
    return random.choice(NSFW_FALLBACK_CONTENT)

# --- Sources ---

SOURCES = [
    {"func": "fetch_random_dog", "weight": 0.5},
    {"func": "fetch_random_cat", "weight": 0.5},
    {"func": "fetch_random_fox", "weight": 0.5},
    {"func": "fetch_random_xkcd", "weight": 0.5},
    {"func": "fetch_random_inaturalist", "weight": 0.5},
    {"func": "fetch_random_fact", "weight": 0.5},
    {"func": "fetch_random_wikipedia", "weight": 0.5},
    {"func": "fetch_random_inspirobot", "weight": 0.5},
    {"func": "fetch_random_pokemon", "weight": 0.5},
    {"func": "fetch_random_quote", "weight": 0.5},
    {"func": "fetch_random_joke", "weight": 0.5},
    {"func": "fetch_random_user", "weight": 0.5},
    {"func": "fetch_random_meme", "weight": 0.5},
    {"func": "fetch_random_trivia", "weight": 0.5},
]

if ENABLE_NSFW:
    SOURCES.extend([
        {"func": "fetch_random_nsfw_anime", "weight": 0.5},  # Higher weight for NSFW
        {"func": "fetch_nsfw_waifuim_tagged", "weight": 0.5},
        {"func": "fetch_nsfw_nekos_best", "weight": 0.5}
    ])

# --- Fallback Content ---

SFW_FALLBACK_CONTENT = [
    {"title": "The Useless Web", "url": "https://theuselessweb.com", "source": "Fallback"},
    {"title": "Random Fact", "description": "A group of flamingos is called a flamboyance.", "source": "Fallback"},
    {"title": "jokette’s Chaos", "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/jokette_card.jpg/320px-jokette_card.jpg", "source": "Fallback"}
]

NSFW_FALLBACK_CONTENT = [
    {"title": "NSFW Fallback: Anime Waifu", "image": "https://example.com/nsfw_waifu1.jpg", "source": "Fallback", "source_url": "https://example.com"},
    {"title": "NSFW Fallback: Hentai Art", "image": "https://example.com/nsfw_hentai1.jpg", "source": "Fallback", "source_url": "https://example.com"},
    {"title": "NSFW Fallback: Ecchi Scene", "image": "https://example.com/nsfw_ecchi1.jpg", "source": "Fallback", "source_url": "https://example.com"}
]

# --- Custom Messages ---

SFW_MESSAGES = [
    "New jokette Drop incoming!",
    "Random awesomeness, just for you!",
    "Surprise drop from the jokette!",
    "Fresh chaos, hot off the press!",
    "jokette’s latest wild find!",
    "A sprinkle of randomness lands!",
    "Hold onto your hats—jokette strikes!",
    "Random treasure, jokette style!",
    "Unleashing a wild drop now!",
    "jokette’s quirky pick of the day!"
]

NSFW_MESSAGES = [
    "⚠️ NSFW Alert! Peek at your peril!",
    "Spicy jokette drop—NSFW warning!",
    "NSFW chaos incoming—brace yourself!",
    "jokette’s naughty surprise awaits!",
    "Not for the faint—NSFW drop!",
    "Risky business: NSFW from jokette!",
    "NSFW delight—enter if you dare!",
    "jokette’s wild side unleashed (NSFW)!",
    "Caution: NSFW randomness ahead!",
    "Spicy and NSFW—jokette delivers!"
]

# --- AI Message Function ---

def get_ai_message(data, max_retries=2):
    """Generates a tailored AI message for the content."""
    if not GEMINI_API_KEY:
        return "AI flair unavailable—no Gemini key!"
    content_type = data.get("title", "random content")
    prompt = f"Write a fun, short, witty message for a {content_type} drop from jokette bot. Keep it under 30 words."
    for attempt in range(max_retries):
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            error_msg = str(e)
            print(f"AI message error (attempt {attempt+1}): {error_msg}")
            if "timeout" in error_msg or "502" in error_msg or "503" in error_msg:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            break
    return "AI oops—enjoy the drop anyway!"

# --- Embed Builder ---

def build_embed(data):
    """Creates a rich Discord embed with source link."""
    embed = {
        "title": data.get("title", "Random jokette Drop"),
        "color": random.choice([0xFF00FF, 0x00FFFF, 0xFFFF00, 0x00FF00, 0xFF0000, 0x0000FF]),
        "footer": {"text": f"jokette Project | Source: {data.get('source', 'Unknown')}"},
        "timestamp": datetime.utcnow().isoformat()
    }
    if "description" in data:
        embed["description"] = data["description"]
    if "image" in data and data["image"]:
        embed["image"] = {"url": data["image"]}
    if "url" in data:
        embed["url"] = data["url"]
    if "source_url" in data:
        embed["fields"] = [{"name": "Explore More", "value": data["source_url"], "inline": True}]
    return {"embeds": [embed]}

# --- Main Function ---

def main():
    """Fetches and posts random content with robust NSFW handling."""
    global cache
    print("jokette bot revving up...")
    if not GEMINI_API_KEY:
        print("Warning: No GEMINI_API_KEY—AI messages off.")
    
    weights = load_weights()
    cache = load_cache()
    tries = 0
    max_tries = len(SOURCES) * 2
    success = False
    used_sources = []

    while tries < max_tries and not success:
        try:
            current_weights = [weights.get(s["func"], s["weight"]) for s in SOURCES]
            source = random.choices(SOURCES, weights=current_weights, k=1)[0]
            print(f"Selected source: {source['func']}")
            if source["func"] in used_sources:
                tries += 1
                continue
            used_sources.append(source["func"])
            fetch_func = globals().get(source["func"])
            if not fetch_func:
                print(f"[!] Function {source['func']} missing!")
                tries += 1
                continue
            data = fetch_func()
            print(f"Fetch result: {data}")
            if data and (data.get("image") or data.get("url") or data.get("description")):
                if "nsfw" not in source["func"].lower():  # Only adjust weights for SFW
                    weights[source["func"]] = min(weights.get(source["func"], source["weight"]) + 0.1, 1.0)
                payload = build_embed(data)
                base_message = random.choice(NSFW_MESSAGES if "nsfw" in source["func"].lower() else SFW_MESSAGES)
                ai_message = get_ai_message(data)
                payload["content"] = f"{base_message}\n\n{ai_message}"
                try:
                    r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                    r.raise_for_status()
                    success = True
                    print(f"Posted: {data.get('title', 'No Title')} from {data.get('source', 'Unknown')}")
                except Exception as e:
                    print(f"Discord post failed: {e}")
                    tries += 1
                    time.sleep(1)
            else:
                if "nsfw" not in source["func"].lower():  # Only adjust weights for SFW
                    weights[source["func"]] = max(weights.get(source["func"], source["weight"]) * 0.5, 0.1)
                print(f"[!] {source['func']} gave no data.")
                tries += 1
                time.sleep(1)
        except Exception as e:
            print(f"Loop error: {e}")
            tries += 1
            time.sleep(1)

    if not success:
        data = random.choice(NSFW_FALLBACK_CONTENT if ENABLE_NSFW else SFW_FALLBACK_CONTENT)
        payload = build_embed(data)
        payload["content"] = "jokette crashed—here’s a backup plan!"
        try:
            requests.post(WEBHOOK_URL, json=payload, timeout=10)
            print("Fallback posted successfully.")
        except Exception as e:
            print(f"Fallback failed too: {e}")

    save_weights(weights)
    save_cache(cache)

if __name__ == "__main__":
    main()

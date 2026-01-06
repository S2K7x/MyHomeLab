import os
import subprocess

# --- CONFIGURATION MISE À JOUR ---
DOCKERFILE_CONTENT = """FROM node:20-bookworm
RUN apt-get update && apt-get install -y \\
    python3 python3-pip python3-dev build-essential \\
    libffi-dev libssl-dev libjpeg-dev zlib1g-dev \\
    curl jq && \\
    rm -rf /var/lib/apt/lists/*
RUN npm install -g n8n
RUN pip3 install --no-cache-dir --break-system-packages \\
    aiohttp aiosqlite beautifulsoup4 cloudflared discord.py dnspython \\
    feedparser google-api-python-client google-generativeai google-genai \\
    httpx orjson pillow pydantic python-dotenv PyYAML qrcode requests \\
    rich schedule websockets whois
ENV N8N_PORT=5678
EXPOSE 5678
CMD ["n8n", "start"]
"""

DOCKER_COMPOSE_CONTENT = """services:
  n8n:
    build: .
    container_name: n8n_rpi5
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - TZ=Europe/Paris
      - N8N_PROTOCOL=http
      - N8N_SECURE_COOKIE=false
      - N8N_PYTHON_ENABLED=true
      - N8N_PYTHON_ALLOW_EXTERNAL=*
      - NODES_EXCLUDE=[]
      - NODE_FUNCTION_ALLOW_EXTERNAL=*
      - N8N_BLOCK_FS=false
    volumes:
      - ./data:/root/.n8n
      - /home/rasberry:/root/rasberry_home
"""

def setup():
    print("📝 Mise à jour de la configuration (Activation du nœud Execute Command)...")
    with open("Dockerfile", "w") as f: f.write(DOCKERFILE_CONTENT)
    with open("docker-compose.yml", "w") as f: f.write(DOCKER_COMPOSE_CONTENT)
    
    print("⚙️ Redémarrage de n8n...")
    try:
        subprocess.run(["docker", "compose", "up", "-d", "--build"], check=True)
        print("\n✅ Configuration terminée ! Relance ton navigateur.")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    setup()
# Config 

Here is the config of my rasberry pi 500
Os: Rasberry Lite 
- Docker 
- Nextcloud 
- Automations with N8N 
- Pihole 

## Commands: 

### Tailscale:
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

### PiHole: 
curl -sSL https://install.pi-hole.net | bash

### Docker: 
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo usermod -aG docker $USER

### Portainer: 
docker volume create portainer_data
docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always \
-v /var/run/docker.sock:/var/run/docker.sock \
-v portainer_data:/data \
portainer/portainer-ce:latest

# n8n
mkdir ~/n8n-docker
cd ~/n8n-docker

docker run -d --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  --restart always \
  docker.n8n.io/n8nio/n8n
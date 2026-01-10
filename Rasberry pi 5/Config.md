# Config 

Here is the config of my rasberry pi 500
Os: Rasberry Lite 
- Docker 
- Nextcloud 
- Automations with N8N 
- Pihole 

## Commands to fully install it: 

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

## Specification: 
Broadcom BCM2712 2.4GHz quad-core 64-bit Arm Cortex-A76 CPU, with cryptography extensions, 512KB per-core L2 caches and a 2MB shared L3 cache

VideoCore VII GPU, supporting OpenGL ES 3.1, Vulkan 1.3

Dual 4Kp60 HDMI® display output with HDR support

4Kp60 HEVC decoder

LPDDR4X-4267 SDRAM (1GB, 2GB, 4GB, 8GB, and 16GB)

Dual-band 802.11ac Wi-Fi®

Bluetooth 5.0 / Bluetooth Low Energy (BLE)

microSD card slot, with support for high-speed SDR104 mode

2 × USB 3.0 ports, supporting simultaneous 5Gbps operation

2 × USB 2.0 ports

Gigabit Ethernet, with PoE+ support (requires separate PoE+ HAT)

2 × 4-lane MIPI camera/display transceivers

PCIe 2.0 x1 interface for fast peripherals (requires separate M.2 HAT or other adapter)

5V/5A DC power via USB-C, with Power Delivery support

Raspberry Pi standard 40-pin header

Real-time clock (RTC), powered from external battery

Power button


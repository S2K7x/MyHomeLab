#!/bin/bash

# --- CONFIGURATION ---
WEBHOOK_URL="https://discord.com/api/...."
HOSTNAME=$(hostname)
DATE=$(date +'%d/%m/%Y à %H:%M')

# --- RÉCUPÉRATION DES INFOS ---
# Espace Disque Global
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')
DISK_FREE=$(df -h / | awk 'NR==2 {print $4}')

# RAM
RAM_USAGE=$(free -m | awk 'NR==2 {printf "%s/%sMB (%.2f%%)", $3,$2,$3*100/$2 }')

# Charge CPU (1 min)
CPU_LOAD=$(uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1 | sed 's/ //g')

# Taille Wazuh
WAZUH_LOGS=$(sudo du -sh /var/ossec/logs/ | cut -f1)
WAZUH_INDEXER=$(sudo du -sh /var/lib/wazuh-indexer/ | cut -f1)
WAZUH_TOTAL=$(sudo du -sh /var/ossec/ | cut -f1)

# Sécurité : Tentatives de connexion SSH échouées cette semaine
FAILED_SSH=$(sudo grep "Failed password" /var/log/auth.log | wc -l)

# --- PRÉPARATION DU MESSAGE DISCORD ---
PAYLOAD=$(cat <<EOF
{
  "embeds": [{
    "title": "📊 Rapport Hebdomadaire Serveur : $HOSTNAME",
    "color": 3447003,
    "fields": [
      { "name": "📅 Date", "value": "$DATE", "inline": true },
      { "name": "⏱️ Uptime", "value": "$(uptime -p)", "inline": true },
      { "name": "💽 Disque (/)", "value": "Utilisé: $DISK_USAGE (Reste $DISK_FREE)", "inline": false },
      { "name": "🧠 RAM", "value": "$RAM_USAGE", "inline": true },
      { "name": "⚡ Charge CPU", "value": "$CPU_LOAD", "inline": true },
      { "name": "🛡️ Stockage Wazuh", "value": "Logs: $WAZUH_LOGS\nIndexer: $WAZUH_INDEXER\nTotal: $WAZUH_TOTAL", "inline": false },
      { "name": "⚠️ Sécurité", "value": "$FAILED_SSH tentatives de connexion échouées", "inline": false }
    ],
    "footer": { "text": "Wazuh Health Monitor" }
  }]
}
EOF
)

# --- ENVOI DU WEBHOOK ---
curl -H "Content-Type: application/json" -X POST -d "$PAYLOAD" "$WEBHOOK_URL"

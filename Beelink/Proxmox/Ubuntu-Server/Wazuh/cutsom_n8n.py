#!/usr/bin/env python3
import sys
import json
import requests

# 1. Récupération des arguments envoyés par Wazuh
# sys.argv[1] est le fichier d'alerte temporaire
# sys.argv[3] est l'URL du webhook définie dans ossec.conf
alert_file = sys.argv[1]
hook_url = sys.argv[3]

try:
    # 2. Lecture de l'alerte JSON générée par Wazuh
    with open(alert_file, 'r') as f:
        alert_json = json.load(f)

    # 3. Envoi à n8n avec un timeout de 10s (pour ne pas bloquer Wazuh)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(hook_url, json=alert_json, headers=headers, timeout=10)
    
    # Vérification si l'envoi a réussi
    response.raise_for_status()

except Exception as e:
    # En cas d'erreur, on écrit dans le log de Wazuh
    with open('/var/ossec/logs/integrations.log', 'a') as log_file:
        log_file.write(f"Erreur intégration n8n: {str(e)}\n")
    sys.exit(1)

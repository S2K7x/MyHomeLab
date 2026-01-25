#!/usr/bin/env python3
import sys
import json
import requests

alert_file = sys.argv[1]
hook_url = sys.argv[3]

try:
    with open(alert_file, 'r') as f:
        alert_json = json.load(f)

    headers = {'Content-Type': 'application/json'}
    response = requests.post(hook_url, json=alert_json, headers=headers, timeout=10)
    
    response.raise_for_status()

except Exception as e:
    with open('/var/ossec/logs/integrations.log', 'a') as log_file:
        log_file.write(f"Erreur intégration n8n: {str(e)}\n")
    sys.exit(1)

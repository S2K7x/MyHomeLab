# 🛡️ ALERTE WAZUH
> {{ $json.body.rule.description || "Aucune description" }}

**🔴 Niveau :** {{ $json.body.rule.level || "N/A" }}
**🆔 ID Règle :** {{ $json.body.rule.id || "N/A" }}
**🖥️ Agent :** `{{ $json.body.agent?.name || "N/A" }}`
**👤 Utilisateur :** `{{ $json.body.data?.srcuser || "N/A" }}`
**🌐 IP Source :** `{{ $json.body.data?.srcip || "N/A" }}`

**📖 Log complet :**
```
{{ ($json.body.full_log || "").substring(0, 1000) }}
```
*🕒 {{ $json.body.timestamp || "" }}*


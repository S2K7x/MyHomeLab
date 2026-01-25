# 🛡️ WAZUH ALERT

> {{ $json.body.rule.description || "No description available" }}

**🔴 Level:** {{ $json.body.rule.level || "N/A" }}
**🆔 Rule ID:** {{ $json.body.rule.id || "N/A" }}
**🖥️ Agent:** `{{ $json.body.agent?.name || "N/A" }}`
**👤 User:** `{{ $json.body.data?.srcuser || "N/A" }}`
**🌐 Source IP:** `{{ $json.body.data?.srcip || "N/A" }}`

**📖 Full Log:**

```
{{ ($json.body.full_log || "").substring(0, 1000) }}

```

*🕒 {{ $json.body.timestamp || "" }}*

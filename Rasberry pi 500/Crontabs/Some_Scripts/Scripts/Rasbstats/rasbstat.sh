#!/bin/bash

# RasbStats - Enhanced System Monitoring Script
# Version: 1.1

# --- Load Configuration ---
SCRIPT_VERSION="1.1"

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") Config file $CONFIG_FILE not found. Using defaults." | tee -a "$LOG_FILE"
    WEBHOOK_URL=""
    CPU_TEMP_WARN=65
    CPU_TEMP_CRITICAL=75
    DISK_USAGE_CRITICAL=90
    DISK_PARTITION="/"
    NET_INTERVAL=1
fi

# --- Utility Functions ---
log_error() {
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") $1" | tee -a "$LOG_FILE" >&2
}

get_or_default() {
    local result
    result="$($1 2>/dev/null)"
    if [ $? -ne 0 ] || [ -z "$result" ]; then
        echo "$2"
    else
        echo "$result"
    fi
}

check_internet() {
    ping -c 1 8.8.8.8 >/dev/null 2>&1
    [ $? -eq 0 ] && echo "Connected" || echo "Disconnected"
}

# --- System Info Collection ---
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
HOSTNAME=$(get_or_default "hostname" "unknown")

# 🌡️ CPU Temperature (Raspberry Pi specific)
if command -v vcgencmd >/dev/null 2>&1; then
    TEMP_RAW=$(get_or_default "vcgencmd measure_temp" "temp=unknown")
    TEMP_CLEANED=$(echo "$TEMP_RAW" | grep -oP "[0-9]+\.[0-9]+" || echo "N/A")
else
    TEMP_CLEANED="N/A (Not a Raspberry Pi?)"
fi
TEMP_COLOR=3066993 # Green
if [[ "$TEMP_CLEANED" =~ ^[0-9]+\.[0-9]+$ ]]; then
    if (( $(echo "$TEMP_CLEANED > $CPU_TEMP_CRITICAL" | bc -l) )); then
        TEMP_COLOR=15158332 # Red
    elif (( $(echo "$TEMP_CLEANED > $CPU_TEMP_WARN" | bc -l) )); then
        TEMP_COLOR=15844367 # Yellow
    fi
fi

# 🧠 CPU Load (Parse 1, 5, 15 min averages)
CPU_LOAD_RAW=$(get_or_default "uptime" "N/A")
CPU_LOAD_1=$(echo "$CPU_LOAD_RAW" | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',' || echo "N/A")
CPU_LOAD_5=$(echo "$CPU_LOAD_RAW" | awk -F'load average:' '{print $2}' | awk '{print $2}' | tr -d ',' || echo "N/A")
CPU_LOAD_15=$(echo "$CPU_LOAD_RAW" | awk -F'load average:' '{print $2}' | awk '{print $3}' || echo "N/A")
CPU_LOAD="$CPU_LOAD_1 / $CPU_LOAD_5 / $CPU_LOAD_15"

# 💾 RAM Usage
MEMORY_TOTAL=$(free -h 2>/dev/null | grep Mem | awk '{print $2}' || echo "N/A")
MEMORY_USED=$(free -h 2>/dev/null | grep Mem | awk '{print $3}' || echo "N/A")
MEMORY="${MEMORY_USED}/${MEMORY_TOTAL}"

# 📀 Disk Usage (Configurable partition)
DISK_TOTAL=$(df -h "$DISK_PARTITION" 2>/dev/null | awk 'NR==2 {print $2}' || echo "N/A")
DISK_USED=$(df -h "$DISK_PARTITION" 2>/dev/null | awk 'NR==2 {print $3}' || echo "N/A")
DISK_USAGE_PERCENT=$(df -h "$DISK_PARTITION" 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//' || echo "0")
DISK="${DISK_USED}/${DISK_TOTAL} (${DISK_USAGE_PERCENT}%)"

# ⚡ Throttling Info (Raspberry Pi specific)
if command -v vcgencmd >/dev/null 2>&1; then
    THROTTLED_HEX=$(get_or_default "vcgencmd get_throttled | awk -F= '{print \$2}'" "0xUNKNOWN")
    case "$THROTTLED_HEX" in
        0x0) THROTTLED_STATUS="No throttling" ;;
        0xUNKNOWN) THROTTLED_STATUS="Unknown" ;;
        *) THROTTLED_STATUS="Throttling: \`${THROTTLED_HEX}\`" ;;
    esac
else
    THROTTLED_STATUS="N/A (Not a Raspberry Pi?)"
fi

# 🌐 Network Info
INTERNET_STATUS=$(check_internet)
IP_PRIVATE=$(get_or_default "hostname -I | awk '{print \$1}'" "Unavailable")
IP_PUBLIC=$( [ "$INTERNET_STATUS" = "Connected" ] && curl -s icanhazip.com || echo "Offline")

# 📶 Network Speed (Configurable interval)
IFACE=$(get_or_default "ip route | grep default | awk '{print \$5}'" "eth0")
if [ -d "/sys/class/net/$IFACE" ]; then
    RX_OLD=$(get_or_default "cat /sys/class/net/$IFACE/statistics/rx_bytes" "0")
    TX_OLD=$(get_or_default "cat /sys/class/net/$IFACE/statistics/tx_bytes" "0")
    sleep "$NET_INTERVAL"
    RX_NEW=$(get_or_default "cat /sys/class/net/$IFACE/statistics/rx_bytes" "0")
    TX_NEW=$(get_or_default "cat /sys/class/net/$IFACE/statistics/tx_bytes" "0")
    RX_SPEED_BPS=$(( (RX_NEW - RX_OLD) / NET_INTERVAL ))
    TX_SPEED_BPS=$(( (TX_NEW - TX_OLD) / NET_INTERVAL ))
    RX_SPEED_HUMAN=$(numfmt --to=iec-i --suffix=B/s <<< "$RX_SPEED_BPS" 2>/dev/null || echo "${RX_SPEED_BPS}B/s")
    TX_SPEED_HUMAN=$(numfmt --to=iec-i --suffix=B/s <<< "$TX_SPEED_BPS" 2>/dev/null || echo "${TX_SPEED_BPS}B/s")
else
    log_error "Interface $IFACE not found."
    RX_SPEED_HUMAN="0B/s"
    TX_SPEED_HUMAN="0B/s"
fi

# 🟢 Active Services
ACTIVE_SERVICES_RAW=$(systemctl list-units --type=service --state=running --no-pager --no-legend 2>/dev/null | awk '{print $1}' | head -n 5 || echo "None")
ACTIVE_SERVICES_FORMATTED=$(echo "$ACTIVE_SERVICES_RAW" | sed 's/.service$//g')

# 🔌 Listening Ports
LISTEN_PORTS_RAW=$(ss -tuln 2>/dev/null | awk 'NR>1 {print $1, $5}' | sed 's/::ffff://g' | head -n 5 || echo "None")
LISTEN_PORTS_FORMATTED="$LISTEN_PORTS_RAW"

# ⬆️ Uptime
UPTIME=$(get_or_default "uptime -p" "N/A")

# 🐧 Kernel Version
KERNEL_VERSION=$(get_or_default "uname -r" "N/A")

# 📦 Upgradable Packages (Debian-specific)
UPDATES_COUNT=$(sudo apt update >/dev/null 2>&1 && apt list --upgradable 2>/dev/null | wc -l || echo "N/A")

# 🔄 Pending Reboot
PENDING_REBOOT=$( [ -f /var/run/reboot-required ] && echo "Yes" || echo "No" )

# --- System Health ---
SYSTEM_HEALTH="GOOD"
SUMMARY="All systems nominal"
if [[ "$TEMP_CLEANED" =~ ^[0-9]+\.[0-9]+$ ]]; then
    if (( $(echo "$TEMP_CLEANED > $CPU_TEMP_CRITICAL" | bc -l) )); then
        SYSTEM_HEALTH="CRITICAL"
        SUMMARY="Critical: High CPU Temp!"
    elif (( $(echo "$TEMP_CLEANED > $CPU_TEMP_WARN" | bc -l) )); then
        SYSTEM_HEALTH="WARNING"
        SUMMARY="Warning: CPU Temp elevated"
    fi
fi
if [ "$DISK_USAGE_PERCENT" -ge "$DISK_USAGE_CRITICAL" ]; then
    SYSTEM_HEALTH=$([ "$SYSTEM_HEALTH" = "CRITICAL" ] && echo "CRITICAL" || echo "WARNING")
    SUMMARY="${SUMMARY}, Disk nearly full"
fi
if [ "$THROTTLED_HEX" != "0x0" ] && [ "$THROTTLED_HEX" != "0xUNKNOWN" ]; then
    SYSTEM_HEALTH=$([ "$SYSTEM_HEALTH" = "CRITICAL" ] && echo "CRITICAL" || echo "WARNING")
    SUMMARY="${SUMMARY}, Throttling detected"
fi

# --- Discord Embed ---
GOOD_SENTENCES=(
    "Rasby here with your Pi’s VIP status update!"
    "Your Pi’s chilling like a pro - Rasby approved!"
    "All green lights from Rasby, your tech sidekick!"
)
WARNING_SENTENCES=(
    "Rasby says: Yo, your Pi’s sweating a bit!"
    "Heads-up from Rasby: Something’s funky, check it!"
    "Rasby’s got a yellow flag - take a peek!"
)
CRITICAL_SENTENCES=(
    "Rasby screaming: MAYDAY! Pi’s in meltdown mode!"
    "Red alert! Rasby says your Pi’s on fire (not literally)!"
    "Rasby’s SOS: Save Our System, stat!"
)

case "$SYSTEM_HEALTH" in
    "GOOD") SELECTED_SENTENCES=("${GOOD_SENTENCES[@]}") ;;
    "WARNING") SELECTED_SENTENCES=("${WARNING_SENTENCES[@]}") ;;
    "CRITICAL") SELECTED_SENTENCES=("${CRITICAL_SENTENCES[@]}") ;;
esac
CUSTOM_SENTENCE="${SELECTED_SENTENCES[$((RANDOM % ${#SELECTED_SENTENCES[@]}))]}"

# Random Tech Tip
TECH_TIPS=("Rebooting fixes 90% of issues!" "Cooler Pi = Happier Pi!" "Update me, I love new bits!")
RANDOM_TIP="${TECH_TIPS[$((RANDOM % ${#TECH_TIPS[@]}))]}"

if ! command -v jq >/dev/null 2>&1; then
    log_error "jq not installed. Install it with 'sudo apt install jq'."
    exit 1
fi

JSON_PAYLOAD=$(jq -n \
    --arg hostname "$HOSTNAME" \
    --arg timestamp "$TIMESTAMP" \
    --arg temp "$TEMP_CLEANED" \
    --arg color "$TEMP_COLOR" \
    --arg cpu_load "$CPU_LOAD" \
    --arg memory "$MEMORY" \
    --arg disk "$DISK" \
    --arg throttled "$THROTTLED_STATUS" \
    --arg ip_private "$IP_PRIVATE" \
    --arg ip_public "$IP_PUBLIC" \
    --arg tx_speed "$TX_SPEED_HUMAN" \
    --arg rx_speed "$RX_SPEED_HUMAN" \
    --arg services "$ACTIVE_SERVICES_FORMATTED" \
    --arg ports "$LISTEN_PORTS_FORMATTED" \
    --arg uptime "$UPTIME" \
    --arg kernel "$KERNEL_VERSION" \
    --arg updates "$UPDATES_COUNT" \
    --arg reboot "$PENDING_REBOOT" \
    --arg summary "$SUMMARY" \
    --arg sentence "$CUSTOM_SENTENCE" \
    --arg tip "$RANDOM_TIP" \
    --arg version "$SCRIPT_VERSION" \
    '{
        "embeds": [{
            "title": "📡 Rasby (\($hostname)) System Report",
            "description": $sentence,
            "color": ($color | tonumber),
            "timestamp": $timestamp,
            "fields": [
                {"name": "🌡️ CPU Temp", "value": "`\($temp)°C`", "inline": true},
                {"name": "🧠 CPU Load (1/5/15)", "value": "`\($cpu_load)`", "inline": true},
                {"name": "💾 RAM Usage", "value": "`\($memory)`", "inline": true},
                {"name": "📀 Disk Usage", "value": "`\($disk)`", "inline": true},
                {"name": "⚡ Throttling", "value": "\($throttled)", "inline": true},
                {"name": "⬆️ Uptime", "value": "`\($uptime)`", "inline": true},
                {"name": "🌐 Private IP", "value": "`\($ip_private)`", "inline": true},
                {"name": "🌍 Public IP", "value": "`\($ip_public)`", "inline": true},
                {"name": "📶 Network Speed (Up/Down)", "value": "`\($tx_speed) / \($rx_speed)`", "inline": true},
                {"name": "🐧 Kernel", "value": "`\($kernel)`", "inline": true},
                {"name": "📦 Updates", "value": "`\($updates) available`", "inline": true},
                {"name": "🔄 Reboot Needed", "value": "`\($reboot)`", "inline": true},
                {"name": "🟢 Active Services", "value": "```\n\($services)\n```", "inline": false},
                {"name": "🔌 Listening Ports", "value": "```\n\($ports)\n```", "inline": false},
                {"name": "📋 System Summary", "value": "\($summary)", "inline": false}
            ],
            "footer": {"text": "Rasby v\($version) | Tip: \($tip)"}
        }]
    }') || { log_error "jq failed to generate payload."; exit 1; }

# --- Send to Discord ---
if [ "$INTERNET_STATUS" = "Connected" ]; then
    curl -s -H "Content-Type: application/json" -X POST -d "$JSON_PAYLOAD" "$WEBHOOK_URL" || log_error "Failed to send to Discord."
else
    log_error "No internet connection. Skipping Discord send."
fi
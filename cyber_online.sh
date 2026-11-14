#!/usr/bin/env bash
# CyberQwen-2B Global Online Launcher
# Gives you a free, public HTTPS URL accessible from ANY device, anywhere in the world (no same Wi-Fi needed).

set -e

echo "[*] Checking local Ollama engine..."
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "[!] Ollama is not active. Starting..."
    sudo systemctl start ollama 2>/dev/null || ollama serve > /dev/null 2>&1 &
    sleep 2
fi

# Ensure cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "[*] Installing cloudflared quick tunnel..."
    curl -L -f https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o "$HOME/.local/bin/cloudflared"
    chmod +x "$HOME/.local/bin/cloudflared"
fi

# Cleanup on exit
cleanup() {
    echo ""
    echo "[*] Shutting down WebUI and public tunnel..."
    kill "$WEBUI_PID" 2>/dev/null || true
    kill "$TUNNEL_PID" 2>/dev/null || true
    rm -f /tmp/cf_tunnel.log
    rm -f "$HOME/.cyber_server_url" /tmp/cyber_server_url
    echo "[+] Done. Model is offline."
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Start local WebUI on port 8080
python3 /home/sambuddhapal/CyberQwen-2B/cyber_webui.py > /dev/null 2>&1 &
WEBUI_PID=$!
sleep 1

# 2. Start Cloudflare Tunnel
rm -f /tmp/cf_tunnel.log
cloudflared tunnel --url http://localhost:8080 > /tmp/cf_tunnel.log 2>&1 &
TUNNEL_PID=$!

echo "[*] Generating secure public HTTPS link (takes ~3 seconds)..."

# 3. Wait for the trycloudflare.com URL to appear in the log
FOUND=0
for i in {1..20}; do
    URL=$(grep -o 'https://[-a-zA-Z0-9@:%._+~#=]\+\.trycloudflare\.com' /tmp/cf_tunnel.log | head -n 1 || true)
    if [ -n "$URL" ]; then
        FOUND=1
        break
    fi
    sleep 1
done

if [ "$FOUND" -eq 1 ]; then
    echo "$URL" > "$HOME/.cyber_server_url"
    echo "$URL" > /tmp/cyber_server_url
    if command -v wl-copy > /dev/null 2>&1; then
        echo -n "$URL" | wl-copy 2>/dev/null || true
    fi
    echo ""
    echo "=================================================================="
    echo "   🚀 CyberQwen-2B is LIVE Online!                                "
    echo "=================================================================="
    echo ""
    echo "   👉 Public URL:  $URL"
    echo ""
    echo "=================================================================="
    echo " • Works on Mobile 4G/5G, work Wi-Fi, or ANY device in the world."
    echo " • 100% Free, SSL encrypted, zero cloud cost."
    echo " • Open the link on your phone to chat with CyberQwen."
    echo " • Press Ctrl+C in this terminal when you want to take it down."
    echo "=================================================================="
    echo ""
    # Keep running until user hits Ctrl+C
    wait "$TUNNEL_PID"
else
    echo "[X] Error: Could not generate tunnel. Check internet connection."
    exit 1
fi

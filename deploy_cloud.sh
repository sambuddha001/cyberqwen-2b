#!/usr/bin/env bash
# CyberQwen-2B One-Click Cloud Deployer
# Designed for Lightning.ai, Cloud VMs, and remote servers.
# 100% Automated: installs Ollama, builds CyberQwen-2B, and opens a public HTTPS link.

set -e

echo "=================================================================="
echo "   🚀 CyberQwen-2B One-Click Cloud Setup                         "
echo "=================================================================="

# 1. Install Ollama if missing
if ! command -v ollama &> /dev/null; then
    echo "[*] Installing Ollama engine..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# 2. Install cloudflared if missing
mkdir -p "$HOME/.local/bin"
export PATH="$HOME/.local/bin:$PATH"

if ! command -v cloudflared &> /dev/null; then
    echo "[*] Installing cloudflared quick tunnel..."
    curl -L -f https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o "$HOME/.local/bin/cloudflared"
    chmod +x "$HOME/.local/bin/cloudflared"
fi

# 3. Ensure Ollama service is running
echo "[*] Starting Ollama in background..."
ollama serve > /tmp/ollama.log 2>&1 &
sleep 3

for i in {1..20}; do
    if curl -s http://127.0.0.1:11434/api/tags &> /dev/null; then
        echo "[+] Ollama is active!"
        break
    fi
    sleep 1
done

# 4. Download 84MB LoRA adapter from GitHub Releases if missing
ADAPTER_FILE="cybersec_adapter.gguf"
RELEASE_URL="https://github.com/sambuddha001/cyberqwen-2b/releases/download/v1.0.0/cybersec_adapter.gguf"

if [ ! -f "$ADAPTER_FILE" ]; then
    echo "[*] Downloading fine-tuned LoRA GGUF adapter (84 MB)..."
    curl -L -f --progress-bar -o "$ADAPTER_FILE" "$RELEASE_URL"
    echo "[+] Download complete."
fi

# 5. Build model in Ollama
echo "[*] Building cybersec-qwen in Ollama..."
ollama create cybersec-qwen -f Modelfile

# 6. Launch global online tunnel
echo "[*] Starting WebUI and Cloudflare tunnel..."
chmod +x ./cyber_online.sh
exec ./cyber_online.sh

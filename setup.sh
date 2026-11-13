#!/usr/bin/env bash
# CyberQwen-2B Local Installer & Setup Script

set -e

echo "============================================="
echo "   CyberQwen-2B Setup & Installation         "
echo "============================================="

# 1. Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "[!] Ollama is not installed. Please install it first:"
    echo "    curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "[+] Ollama detected: $(ollama --version)"

# 2. Check if Ollama service is active
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "[*] Starting Ollama server in background..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# 3. Ensure the fine-tuned LoRA GGUF adapter exists (auto-download from GitHub Release if missing)
ADAPTER_FILE="cybersec_adapter.gguf"
RELEASE_URL="https://github.com/sambuddha001/cyberqwen-2b/releases/download/v1.0.0/cybersec_adapter.gguf"

if [ ! -f "$ADAPTER_FILE" ]; then
    echo "[*] Adapter file '$ADAPTER_FILE' not found locally."
    echo "[*] Downloading fine-tuned LoRA GGUF adapter (84 MB) from GitHub Release v1.0.0..."
    if command -v curl &> /dev/null; then
        curl -L -f --progress-bar -o "$ADAPTER_FILE" "$RELEASE_URL"
    elif command -v wget &> /dev/null; then
        wget --show-progress -O "$ADAPTER_FILE" "$RELEASE_URL"
    else
        echo "[X] Error: Neither curl nor wget is installed. Please download $RELEASE_URL manually."
        exit 1
    fi
    echo "[+] Downloaded $ADAPTER_FILE successfully."
else
    echo "[+] Found existing adapter: $ADAPTER_FILE"
fi

# 4. Build the model from Modelfile
echo "[*] Creating cybersec-qwen model in Ollama..."
ollama create cybersec-qwen -f Modelfile

# 5. Create local CLI launcher
LAUNCHER_PATH="$HOME/.local/bin/cyber-qwen"
mkdir -p "$HOME/.local/bin"

cat << 'EOF' > "$LAUNCHER_PATH"
#!/usr/bin/env bash
exec ollama run cybersec-qwen --think=false "$@"
EOF

chmod +x "$LAUNCHER_PATH"
echo "[+] Created CLI launcher at: $LAUNCHER_PATH"

echo "============================================="
echo "   Setup Complete!                           "
echo "   Run the model anytime by typing:          "
echo "       cyber-qwen                            "
echo "============================================="

#!/usr/bin/env python3
"""
CyberQwen-2B Mobile & Multi-Device WebUI
Lightweight, zero-dependency, ChatGPT-style responsive web interface.
Access from any phone, tablet, or PC on your local Wi-Fi or via tunnel.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "cybersec-qwen"
PORT = int(os.environ.get("PORT", 8080))

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>CyberQwen-2B Copilot</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #e6edf3;
      --text-muted: #8b949e;
      --accent: #58a6ff;
      --accent-green: #3fb950;
      --user-msg: #1f6feb;
      --bot-msg: #21262d;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background-color: var(--bg); color: var(--text); display: flex; flex-direction: column; height: 100dvh; overflow: hidden; }
    header {
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      padding: 12px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }
    .header-title { display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 1.1rem; }
    .badge {
      background: rgba(63, 185, 80, 0.15);
      color: var(--accent-green);
      border: 1px solid rgba(63, 185, 80, 0.4);
      font-size: 0.75rem;
      padding: 3px 8px;
      border-radius: 12px;
      font-weight: 500;
    }
    #chat-container {
      flex: 1;
      overflow-y: auto;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      scroll-behavior: smooth;
    }
    .message-row { display: flex; flex-direction: column; max-width: 85%; }
    .message-row.user { align-self: flex-end; align-items: flex-end; }
    .message-row.bot { align-self: flex-start; align-items: flex-start; max-width: 92%; }
    .bubble {
      padding: 12px 16px;
      border-radius: 16px;
      font-size: 0.95rem;
      line-height: 1.5;
      word-break: break-word;
    }
    .user .bubble { background: var(--user-msg); color: #fff; border-bottom-right-radius: 4px; }
    .bot .bubble { background: var(--bot-msg); border: 1px solid var(--border); color: var(--text); border-bottom-left-radius: 4px; }
    pre {
      background: #0d1117;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      overflow-x: auto;
      margin: 8px 0;
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
      font-size: 0.88rem;
    }
    code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: #ff7b72; font-size: 0.9em; }
    pre code { color: #e6edf3; }
    .quick-chips {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 8px 18px;
      background: var(--bg);
      flex-shrink: 0;
      scrollbar-width: none;
    }
    .quick-chips::-webkit-scrollbar { display: none; }
    .chip {
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 6px 12px;
      border-radius: 16px;
      font-size: 0.8rem;
      white-space: nowrap;
      cursor: pointer;
      transition: all 0.2s;
    }
    .chip:hover { border-color: var(--accent); color: var(--text); }
    #input-container {
      background: var(--card-bg);
      border-top: 1px solid var(--border);
      padding: 12px 18px;
      display: flex;
      gap: 10px;
      align-items: flex-end;
      flex-shrink: 0;
    }
    textarea {
      flex: 1;
      background: #0d1117;
      border: 1px solid var(--border);
      border-radius: 12px;
      color: #fff;
      padding: 12px 14px;
      font-size: 0.95rem;
      resize: none;
      max-height: 120px;
      min-height: 44px;
      outline: none;
    }
    textarea:focus { border-color: var(--accent); }
    button {
      background: var(--accent);
      color: #0d1117;
      border: none;
      border-radius: 12px;
      width: 44px;
      height: 44px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: opacity 0.2s;
    }
    button:disabled { opacity: 0.4; cursor: not-allowed; }
    .cursor { display: inline-block; width: 6px; height: 14px; background: var(--accent); margin-left: 2px; animation: blink 1s infinite; vertical-align: middle; }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
  </style>
</head>
<body>
  <header>
    <div class="header-title">
      <span>🛡️ CyberQwen-2B</span>
      <span class="badge">100% Offline</span>
    </div>
    <div style="font-size: 0.75rem; color: var(--text-muted);">Intel i5 • 8GB RAM</div>
  </header>

  <div id="chat-container">
    <div class="message-row bot">
      <div class="bubble">
        👋 <b>CyberQwen-2B is ready.</b><br>
        Ask for exploit mechanics, detection engineering rules (Sigma/YARA), log triage, or script analysis.
      </div>
    </div>
  </div>

  <div class="quick-chips">
    <div class="chip" onclick="quickAsk('Generate a Sigma rule for LSASS dump via Event ID 10')">🕵️ Detect LSASS (Sigma)</div>
    <div class="chip" onclick="quickAsk('Generate a YARA rule for UPX packed PE executables')">🦠 UPX Packed (YARA)</div>
    <div class="chip" onclick="quickAsk('Provide an error-based SQL injection PoC payload and remediation')">💉 Error-based SQLi</div>
    <div class="chip" onclick="quickAsk('How to detect Kerberoasting in Active Directory in 2 bullet points')">🏢 Kerberoasting Triage</div>
  </div>

  <div id="input-container">
    <textarea id="prompt-input" rows="1" placeholder="Ask CyberQwen-2B anything..." onkeydown="handleKey(event)"></textarea>
    <button id="send-btn" onclick="sendMessage()">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
    </button>
  </div>

  <script>
    const chatContainer = document.getElementById('chat-container');
    const promptInput = document.getElementById('prompt-input');
    const sendBtn = document.getElementById('send-btn');

    function escapeHtml(text) {
      return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function formatText(raw) {
      // Basic markdown parser for code blocks and inline code
      let formatted = raw.replace(/```([a-zA-Z0-9_-]*)\\n([\\s\\S]*?)```/g, (match, lang, code) => {
        return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
      });
      formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
      formatted = formatted.replace(/\\n/g, '<br>');
      return formatted;
    }

    function quickAsk(text) {
      promptInput.value = text;
      sendMessage();
    }

    function handleKey(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    }

    async function sendMessage() {
      const prompt = promptInput.value.trim();
      if (!prompt) return;

      // Add user message
      const userRow = document.createElement('div');
      userRow.className = 'message-row user';
      userRow.innerHTML = `<div class="bubble">${escapeHtml(prompt).replace(/\\n/g, '<br>')}</div>`;
      chatContainer.appendChild(userRow);

      promptInput.value = '';
      sendBtn.disabled = true;

      // Add bot message placeholder
      const botRow = document.createElement('div');
      botRow.className = 'message-row bot';
      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      bubble.innerHTML = '<span class="cursor"></span>';
      botRow.appendChild(bubble);
      chatContainer.appendChild(botRow);
      chatContainer.scrollTop = chatContainer.scrollHeight;

      let fullText = '';
      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: prompt })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          const lines = chunk.split('\\n');
          for (const line of lines) {
            if (line.trim()) {
              try {
                const parsed = JSON.parse(line);
                if (parsed.response) {
                  fullText += parsed.response;
                  bubble.innerHTML = formatText(fullText) + '<span class="cursor"></span>';
                  chatContainer.scrollTop = chatContainer.scrollHeight;
                }
              } catch (err) {}
            }
          }
        }
      } catch (err) {
        fullText += `\\n[!] Network or inference error: ${err.message}`;
      } finally {
        bubble.innerHTML = formatText(fullText);
        sendBtn.disabled = false;
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }
  </script>
</body>
</html>
"""

class WebUIHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            prompt = data.get("prompt", "")

            # Forward request to local Ollama instance with thinking bypassed
            ollama_payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": True,
                "think": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9
                }
            }

            req = urllib.request.Request(
                OLLAMA_API_URL,
                data=json.dumps(ollama_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            try:
                with urllib.request.urlopen(req) as resp:
                    for line in resp:
                        self.wfile.write(line)
                        self.wfile.flush()
            except Exception as e:
                err_json = json.dumps({"response": f"\\n[!] Ollama Error: {str(e)}"})
                self.wfile.write(f"{err_json}\\n".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\\n")

def run():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), WebUIHandler)
    print("=" * 60)
    print("   CyberQwen-2B Multi-Device WebUI is Running!       ")
    print("=" * 60)
    print(f"[*] Local access on this laptop:  http://localhost:{PORT}")
    print(f"[*] Access from phone/tablet/PC:  http://192.168.1.11:{PORT}")
    print("=" * 60)
    print("[*] Press Ctrl+C in this terminal to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\n[+] Server stopped.")
        sys.exit(0)

if __name__ == "__main__":
    run()

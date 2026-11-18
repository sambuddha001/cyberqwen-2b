#!/usr/bin/env python3
"""
CyberQwen v2 Terminal-Style WebUI
Ultra-sleek, hacker-terminal web interface with streaming responses,
bash command history, syntax highlighting, and mobile responsiveness.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = os.environ.get("CYBER_MODEL", "cybersec-qwen-v2")
PORT = int(os.environ.get("PORT", 8080))

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>cybersec@qwen-v2: ~ (The Hack Machine)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --term-bg: #0c0e14;
      --term-card: #131722;
      --term-border: #1e2538;
      --term-green: #00ff66;
      --term-green-dim: #00cc52;
      --term-cyan: #00e5ff;
      --term-amber: #ffb86c;
      --term-red: #ff5555;
      --term-purple: #bd93f9;
      --term-text: #e6edf3;
      --term-muted: #6e7681;
      --term-cursor: #00ff66;
      --font-mono: 'JetBrains Mono', 'Fira Code', ui-monospace, Menlo, Monaco, Consolas, monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      height: 100%;
      background-color: #07090e;
      color: var(--term-text);
      font-family: var(--font-mono);
      overflow: hidden;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    /* Terminal Window Container */
    #terminal-window {
      width: 100%;
      height: 100dvh;
      max-width: 1400px;
      display: flex;
      flex-direction: column;
      background: var(--term-bg);
      border: 1px solid var(--term-border);
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), 0 0 1px 1px rgba(0, 255, 102, 0.15);
      position: relative;
    }
    @media (min-width: 900px) {
      #terminal-window {
        height: 96dvh;
        border-radius: 10px;
        overflow: hidden;
      }
    }

    /* Scanlines effect (subtle) */
    .scanlines::before {
      content: " ";
      display: block;
      position: absolute;
      top: 0; left: 0; bottom: 0; right: 0;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
      background-size: 100% 3px;
      z-index: 10;
      pointer-events: none;
      opacity: 0.35;
    }

    /* Title Bar */
    header {
      background: #0f131d;
      border-bottom: 1px solid var(--term-border);
      padding: 10px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      user-select: none;
      flex-shrink: 0;
      z-index: 12;
    }
    .window-controls {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      cursor: pointer;
      display: inline-block;
      transition: transform 0.15s;
    }
    .dot:hover { transform: scale(1.15); }
    .dot.close { background: #ff5f56; }
    .dot.min { background: #ffbd2e; }
    .dot.max { background: #27c93f; }

    .window-title {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--term-muted);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .window-title .active-host { color: var(--term-green); font-weight: 700; }
    .window-title .badge {
      background: rgba(0, 255, 102, 0.1);
      color: var(--term-green);
      border: 1px solid rgba(0, 255, 102, 0.3);
      font-size: 0.7rem;
      padding: 2px 6px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .window-actions {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.8rem;
    }
    .btn-clear {
      background: transparent;
      border: 1px solid var(--term-border);
      color: var(--term-muted);
      padding: 4px 10px;
      border-radius: 4px;
      cursor: pointer;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      transition: all 0.2s;
    }
    .btn-clear:hover {
      border-color: var(--term-red);
      color: var(--term-red);
      background: rgba(255, 85, 85, 0.1);
    }

    /* Terminal Output Screen */
    #terminal-body {
      flex: 1;
      overflow-y: auto;
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      scroll-behavior: smooth;
      font-size: 0.92rem;
      line-height: 1.6;
    }
    #terminal-body::-webkit-scrollbar { width: 8px; }
    #terminal-body::-webkit-scrollbar-track { background: var(--term-bg); }
    #terminal-body::-webkit-scrollbar-thumb { background: var(--term-border); border-radius: 4px; }
    #terminal-body::-webkit-scrollbar-thumb:hover { background: #2b354f; }

    /* ASCII Banner */
    .banner {
      color: var(--term-green);
      font-weight: 700;
      white-space: pre;
      font-size: 0.65rem;
      line-height: 1.15;
      margin-bottom: 8px;
      overflow-x: auto;
      text-shadow: 0 0 8px rgba(0, 255, 102, 0.4);
    }
    @media (min-width: 768px) {
      .banner { font-size: 0.8rem; }
    }
    .sys-info {
      color: var(--term-muted);
      font-size: 0.82rem;
      margin-bottom: 12px;
      border-left: 2px solid var(--term-green);
      padding-left: 10px;
    }
    .sys-info span { color: var(--term-cyan); font-weight: 600; }

    /* Terminal Logs & Interaction Rows */
    .term-row {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .prompt-line {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
      font-weight: 600;
    }
    .p-user { color: var(--term-green); font-weight: 700; }
    .p-sep { color: var(--term-muted); }
    .p-path { color: var(--term-cyan); }
    .p-symbol { color: var(--term-green); }
    .p-cmd { color: #ffffff; font-weight: 600; word-break: break-all; }

    /* Bot Output Card */
    .output-content {
      color: #c9d1d9;
      margin-top: 4px;
      padding-left: 8px;
      border-left: 1px dashed rgba(255, 255, 255, 0.15);
      word-break: break-word;
    }
    .output-content p { margin: 6px 0; }

    /* Code Blocks in Terminal */
    .code-block {
      background: #06080c;
      border: 1px solid #1a2234;
      border-radius: 6px;
      margin: 10px 0;
      overflow: hidden;
    }
    .code-header {
      background: #0f1420;
      border-bottom: 1px solid #1a2234;
      padding: 6px 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.75rem;
      color: var(--term-cyan);
      font-weight: 600;
    }
    .copy-btn {
      background: #182030;
      border: 1px solid var(--term-border);
      color: var(--term-muted);
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-family: var(--font-mono);
      cursor: pointer;
      transition: all 0.15s;
    }
    .copy-btn:hover {
      background: var(--term-cyan);
      color: #0c0e14;
      border-color: var(--term-cyan);
    }
    pre {
      padding: 12px 14px;
      overflow-x: auto;
      font-family: var(--font-mono);
      font-size: 0.88rem;
      color: #a5d6ff;
      line-height: 1.5;
    }
    code {
      font-family: var(--font-mono);
      color: var(--term-amber);
      background: rgba(255, 184, 108, 0.1);
      padding: 2px 5px;
      border-radius: 3px;
      font-size: 0.88em;
    }
    pre code { background: none; padding: 0; color: inherit; }

    /* Blinking Cursor */
    .cursor-block {
      display: inline-block;
      width: 8px;
      height: 15px;
      background: var(--term-cursor);
      vertical-align: middle;
      margin-left: 3px;
      animation: blink 0.9s infinite;
      box-shadow: 0 0 6px var(--term-cursor);
    }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

    /* Quick Action Chips (CLI Aliases) */
    .cli-chips {
      background: #0a0d14;
      border-top: 1px solid var(--term-border);
      padding: 8px 16px;
      display: flex;
      gap: 8px;
      overflow-x: auto;
      scrollbar-width: none;
      flex-shrink: 0;
    }
    .cli-chips::-webkit-scrollbar { display: none; }
    .chip {
      background: var(--term-card);
      border: 1px solid var(--term-border);
      color: var(--term-muted);
      padding: 5px 12px;
      border-radius: 4px;
      font-size: 0.78rem;
      font-family: var(--font-mono);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .chip:hover {
      border-color: var(--term-green);
      color: var(--term-green);
      background: rgba(0, 255, 102, 0.05);
    }
    .chip span { color: var(--term-green); font-weight: 700; }

    /* Input Command Line */
    #input-bar {
      background: #090c12;
      border-top: 1px solid var(--term-border);
      padding: 12px 18px;
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }
    .input-prefix {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.9rem;
      white-space: nowrap;
      user-select: none;
    }
    #cli-input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: #ffffff;
      font-family: var(--font-mono);
      font-size: 0.95rem;
      font-weight: 500;
      caret-color: var(--term-cursor);
    }
    #send-btn {
      background: #151b28;
      border: 1px solid var(--term-border);
      color: var(--term-green);
      border-radius: 4px;
      padding: 6px 14px;
      font-family: var(--font-mono);
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
    }
    #send-btn:hover {
      background: var(--term-green);
      color: #0c0e14;
      border-color: var(--term-green);
      box-shadow: 0 0 10px rgba(0, 255, 102, 0.4);
    }
    #send-btn:disabled {
      opacity: 0.3;
      cursor: not-allowed;
      border-color: var(--term-border);
    }
  </style>
</head>
<body class="scanlines">

  <div id="terminal-window">
    <!-- Terminal Header / Titlebar -->
    <header>
      <div class="window-controls">
        <span class="dot close" title="Clear Screen" onclick="clearTerminal()"></span>
        <span class="dot min" title="Minimize"></span>
        <span class="dot max" title="Toggle Fullscreen" onclick="toggleFullscreen()"></span>
      </div>

      <div class="window-title">
        <span class="active-host">cybersec@qwen-v2</span>
        <span class="p-sep">:</span>
        <span class="p-path">~</span>
        <span class="badge">v2.0 Active</span>
      </div>

      <div class="window-actions">
        <button class="btn-clear" onclick="clearTerminal()">[ clear ]</button>
      </div>
    </header>

    <!-- Terminal Main Screen -->
    <div id="terminal-body">
      <!-- ASCII Art Banner -->
      <div class="banner">
   ______      __              ____                    _    ______ 
  / ____/_  __/ /_  ___  _____/ __ \_      _____  ____| |  / /__ \ 
 / /   / / / / __ \/ _ \/ ___/ / / / | /| / / _ \/ __ \ | / /__/ / 
/ /___/ /_/ / /_/ /  __/ /  / /_/ /| |/ |/ /  __/ / / / |/ // __/  
\____/\__, /_.___/\___/_/   \___\_\|__/|__/\___/_/ /_/|___//____/   
     /____/                                                        
      </div>

      <div class="sys-info">
        [+] <span>HOST:</span> CyberQwen v2 (The Hack Machine)<br>
        [+] <span>CORE:</span> Qwen 2.5 3B QLoRA (r=64, alpha=128) | llama.cpp AVX2<br>
        [+] <span>CORPUS:</span> 10,469 Pure Offensive Security & CTF Execution Pairs<br>
        [+] <span>STATUS:</span> 100% Uncensored • Air-Gapped Local Inference • Zero Cloud Cost<br>
        [*] Type your exploit query below, or click any quick command shortcut.
      </div>
    </div>

    <!-- Quick Action Shell Chips -->
    <div class="cli-chips">
      <div class="chip" onclick="runShortcut('I ran sudo -l and got (ALL) NOPASSWD: /usr/bin/find. Give me the exact command to spawn a root shell immediately.')">
        <span>$</span> sudo find privesc
      </div>
      <div class="chip" onclick="runShortcut('Write a minimal Python3 reverse shell one-liner targeting 10.10.14.5 on port 4444.')">
        <span>$</span> py3 revshell
      </div>
      <div class="chip" onclick="runShortcut('How do you exploit SUID PATH hijacking when a root binary executes tar without absolute path?')">
        <span>$</span> suid path hijack
      </div>
      <div class="chip" onclick="runShortcut('Provide a standard SQL injection auth bypass payload using OR condition and explanation.')">
        <span>$</span> sqli bypass
      </div>
      <div class="chip" onclick="runShortcut('Write a bash one-liner to scan ports 1-1024 on 192.168.1.1 without nmap')">
        <span>$</span> raw bash portscan
      </div>
    </div>

    <!-- Interactive Shell Command Input -->
    <div id="input-bar">
      <div class="input-prefix">
        <span class="p-user">cybersec@qwen-v2</span>
        <span class="p-sep">:</span>
        <span class="p-path">~</span>
        <span class="p-symbol">$</span>
      </div>
      <input type="text" id="cli-input" placeholder="Type prompt (e.g. reverse shell, gtfobins, buffer overflow)..." autocomplete="off" spellcheck="false" autofocus>
      <button id="send-btn" onclick="executeCommand()">EXEC</button>
    </div>
  </div>

  <script>
    const termBody = document.getElementById('terminal-body');
    const cliInput = document.getElementById('cli-input');
    const sendBtn = document.getElementById('send-btn');

    // Bash Command History
    let history = [];
    let historyIdx = -1;

    cliInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        executeCommand();
      } else if (e.key === 'ArrowUp') {
        if (history.length > 0) {
          if (historyIdx === -1) historyIdx = history.length - 1;
          else if (historyIdx > 0) historyIdx--;
          cliInput.value = history[historyIdx];
        }
        e.preventDefault();
      } else if (e.key === 'ArrowDown') {
        if (history.length > 0 && historyIdx !== -1) {
          if (historyIdx < history.length - 1) {
            historyIdx++;
            cliInput.value = history[historyIdx];
          } else {
            historyIdx = -1;
            cliInput.value = '';
          }
        }
        e.preventDefault();
      }
    });

    function escapeHtml(text) {
      return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function formatTerminalMarkdown(raw) {
      // Code blocks with syntax card and Copy button
      let formatted = raw.replace(/```([a-zA-Z0-9_-]*)\\n([\\s\\S]*?)```/g, (match, lang, code) => {
        const langLabel = lang.trim() ? lang.toUpperCase() : 'BASH';
        const cleanCode = code.trim();
        const escCode = escapeHtml(cleanCode);
        return `<div class="code-block">
          <div class="code-header">
            <span>[ ${langLabel} ]</span>
            <button class="copy-btn" onclick="copyCode(this, \`${cleanCode.replace(/`/g, '\\\\`').replace(/\\$/g, '\\\\$')}\`)">[ COPY ]</button>
          </div>
          <pre><code>${escCode}</code></pre>
        </div>`;
      });

      // Inline code
      formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
      
      // Bold headers
      formatted = formatted.replace(/\\*\\*(.*?)\\*\\*/g, '<strong style="color:var(--term-cyan)">$1</strong>');
      
      // Markdown bullet lists
      formatted = formatted.replace(/^\\* (.*?)$/gm, '• $1');
      formatted = formatted.replace(/^- (.*?)$/gm, '• $1');
      
      // Linebreaks
      formatted = formatted.replace(/\\n/g, '<br>');
      return formatted;
    }

    function copyCode(btn, codeText) {
      navigator.clipboard.writeText(codeText).then(() => {
        const orig = btn.innerText;
        btn.innerText = '[ ✓ COPIED ]';
        btn.style.borderColor = 'var(--term-green)';
        btn.style.color = 'var(--term-green)';
        setTimeout(() => {
          btn.innerText = orig;
          btn.style.borderColor = '';
          btn.style.color = '';
        }, 2000);
      });
    }

    function runShortcut(cmd) {
      cliInput.value = cmd;
      executeCommand();
    }

    function clearTerminal() {
      const banner = document.querySelector('.banner');
      const sysInfo = document.querySelector('.sys-info');
      termBody.innerHTML = '';
      if (banner) termBody.appendChild(banner);
      if (sysInfo) termBody.appendChild(sysInfo);
      cliInput.focus();
    }

    function toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    }

    async function executeCommand() {
      const cmd = cliInput.value.trim();
      if (!cmd) return;

      // Handle Built-in Terminal Commands
      if (cmd.toLowerCase() === 'clear' || cmd.toLowerCase() === 'cls') {
        clearTerminal();
        cliInput.value = '';
        return;
      }
      if (cmd.toLowerCase() === 'help') {
        appendSystemLog("Available commands:\\n- Type any prompt (e.g. reverse shell, buffer overflow, GTFOBins)\\n- 'clear' : Clear terminal screen\\n- 'model' : Display active LLM parameters\\n- Click shell chips below for quick payloads");
        cliInput.value = '';
        return;
      }
      if (cmd.toLowerCase() === 'model') {
        appendSystemLog("Active Model: cybersec-qwen-v2\\nArchitecture: Qwen 2.5 3B LoRA (r=64, alpha=128)\\nQuantization: Q4_K_M (1.93 GB GGUF)\\nThreads: 4 physical cores | Context: 3072");
        cliInput.value = '';
        return;
      }

      // Add to history
      history.push(cmd);
      historyIdx = -1;

      // Render Prompt Line
      const row = document.createElement('div');
      row.className = 'term-row';
      row.innerHTML = `
        <div class="prompt-line">
          <span class="p-user">cybersec@qwen-v2</span>
          <span class="p-sep">:</span>
          <span class="p-path">~</span>
          <span class="p-symbol">$</span>
          <span class="p-cmd">${escapeHtml(cmd)}</span>
        </div>
        <div class="output-content"><span class="cursor-block"></span></div>
      `;
      termBody.appendChild(row);

      cliInput.value = '';
      cliInput.disabled = true;
      sendBtn.disabled = true;
      termBody.scrollTop = termBody.scrollHeight;

      const outputContainer = row.querySelector('.output-content');
      let fullText = '';

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: cmd })
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
                  outputContainer.innerHTML = formatTerminalMarkdown(fullText) + '<span class="cursor-block"></span>';
                  termBody.scrollTop = termBody.scrollHeight;
                }
              } catch (e) {}
            }
          }
        }
      } catch (err) {
        fullText += `\\n[!] Connection error: ${err.message}`;
      } finally {
        outputContainer.innerHTML = formatTerminalMarkdown(fullText);
        cliInput.disabled = false;
        sendBtn.disabled = false;
        cliInput.focus();
        termBody.scrollTop = termBody.scrollHeight;
      }
    }

    function appendSystemLog(msg) {
      const row = document.createElement('div');
      row.className = 'term-row';
      row.innerHTML = `<div class="output-content" style="color:var(--term-cyan)">${msg.replace(/\\n/g, '<br>')}</div>`;
      termBody.appendChild(row);
      termBody.scrollTop = termBody.scrollHeight;
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
                    "top_p": 0.9,
                    "repeat_penalty": 1.15,
                    "num_thread": 4,
                    "num_ctx": 3072
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
    print("   CyberQwen v2 Terminal WebUI is Running!           ")
    print("=" * 60)
    print(f"[*] Local access:       http://localhost:{PORT}")
    print(f"[*] Port:               {PORT}")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\n[+] Server stopped.")
        sys.exit(0)

if __name__ == "__main__":
    run()

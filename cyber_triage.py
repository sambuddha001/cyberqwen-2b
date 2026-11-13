#!/usr/bin/env python3
"""
CyberQwen Triage & Automation Client
Zero-dependency Python CLI for automated security analysis, log triage, and rule generation.
"""

import sys
import json
import argparse
import urllib.request
import urllib.error

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "cybersec-qwen"

def query_model(prompt: str, stream: bool = True) -> str:
    """Send prompt to local Ollama instance and stream/return response."""
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9
        }
    }

    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    full_response = []
    try:
        with urllib.request.urlopen(req) as response:
            if stream:
                for line in response:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        text = chunk.get("response", "")
                        print(text, end="", flush=True)
                        full_response.append(text)
                print()
            else:
                body = json.loads(response.read().decode("utf-8"))
                return body.get("response", "")
    except urllib.error.URLError as e:
        print(f"\n[!] Error connecting to Ollama: {e}")
        print("    Ensure Ollama is running (`ollama serve`)")
        sys.exit(1)

    return "".join(full_response)

def main():
    parser = argparse.ArgumentParser(description="CyberQwen-2B Local Triage Assistant")
    parser.add_argument("-q", "--query", type=str, help="Ask a direct cybersecurity question")
    parser.add_argument("--analyze-log", action="store_true", help="Analyze log piped from stdin")
    parser.add_argument("--generate-yara", type=str, help="Generate YARA rule for target threat description")
    parser.add_argument("--generate-sigma", type=str, help="Generate Sigma detection rule for target event")

    args = parser.parse_args()

    if args.analyze_log:
        print("[*] Reading log input from stdin...")
        log_content = sys.stdin.read().strip()
        if not log_content:
            print("[!] Empty stdin. Pipe logs via: `cat logfile.log | python3 cyber_triage.py --analyze-log`")
            sys.exit(1)
        prompt = f"Analyze the following raw security event logs. Extract IOCs, assess threat level, and recommend immediate defensive triage steps:\n\n```\n{log_content}\n```"
        query_model(prompt)

    elif args.generate_yara:
        prompt = f"Generate a syntactically valid, production-ready YARA rule to detect: {args.generate_yara}. Include meta, strings, and condition."
        query_model(prompt)

    elif args.generate_sigma:
        prompt = f"Generate a production-ready Sigma rule in YAML format to detect: {args.generate_sigma}. Include title, status, logsource, detection, and level."
        query_model(prompt)

    elif args.query:
        query_model(args.query)

    else:
        # Interactive mode
        print("==================================================")
        print("  CyberQwen-2B Interactive Security Copilot      ")
        print("  Type 'exit' or 'quit' to end session.          ")
        print("==================================================\n")
        while True:
            try:
                user_input = input("cyber-qwen> ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit"):
                    break
                print("\nAssistant:")
                query_model(user_input)
                print()
            except (KeyboardInterrupt, EOFError):
                print("\nSession ended.")
                break

if __name__ == "__main__":
    main()

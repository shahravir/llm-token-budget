"""
Ollama-first router: try local model for small tasks; set escalate=True for frontier.
Requires: ollama serve && ollama pull qwen2.5-coder:7b
"""

from __future__ import annotations

import json
import os
import sys

import httpx

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
LOCAL_MODEL = os.environ.get("LOCAL_MODEL", "qwen2.5-coder:7b")
MAX_LOCAL_CHARS = int(os.environ.get("MAX_LOCAL_CHARS", "12000"))


def ask_local(prompt: str, system: str = "") -> tuple[str, bool]:
    """
    Returns (response_text, should_escalate).
    Escalate when prompt too large or model signals low confidence.
    """
    if len(prompt) > MAX_LOCAL_CHARS:
        return "", True

    payload = {
        "model": LOCAL_MODEL,
        "messages": [
            {"role": "system", "content": system or "Answer tersely. If unsure, start with ESCALATE:"},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    try:
        r = httpx.post(OLLAMA_URL, json=payload, timeout=120.0)
        r.raise_for_status()
    except httpx.HTTPError as e:
        return f"(ollama unavailable: {e})", True

    content = r.json().get("message", {}).get("content", "")
    escalate = content.strip().upper().startswith("ESCALATE:") or "not sure" in content.lower()[:80]
    return content, escalate


def run_task(prompt: str, system: str = "") -> dict:
    text, escalate = ask_local(prompt, system)
    return {
        "tier": "frontier" if escalate else "local",
        "model": None if escalate else LOCAL_MODEL,
        "text": text,
        "escalate": escalate,
    }


if __name__ == "__main__":
    demo = sys.argv[1] if len(sys.argv) > 1 else "Write a one-line commit message for: fix null check in auth refresh"
    result = run_task(demo)
    print(json.dumps(result, indent=2))

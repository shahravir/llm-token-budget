"""
Fit a list of context blocks under a token budget.
Higher priority blocks are kept; lower priority blocks are truncated or dropped.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common_tokens import count_tokens, truncate_to_tokens


def fit_context(
    blocks: list[tuple[str, int, str]],
    max_tokens: int,
) -> list[str]:
    """
    blocks: list of (label, priority, text) — higher priority kept first.
    Returns selected block texts in priority order.
    """
    ordered = sorted(blocks, key=lambda b: b[1], reverse=True)
    kept: list[str] = []
    used = 0

    for label, _prio, text in ordered:
        tokens = count_tokens(text)
        remaining = max_tokens - used
        if remaining <= 0:
            break
        if tokens <= remaining:
            kept.append(text)
            used += tokens
            continue
        kept.append(truncate_to_tokens(text, remaining))
        used += count_tokens(kept[-1])
        break

    return kept


if __name__ == "__main__":
    blocks = [
        ("system_rules", 100, "You are a senior engineer. Follow repo AGENTS.md."),
        ("user_task", 90, "Fix null pointer in auth refresh handler."),
        ("stack_trace", 80, "Traceback (most recent call last):\n  File auth.py:42 ..."),
        ("full_file_auth", 50, open(__file__).read() * 3 if False else "# auth.py\n" + ("x = 1\n" * 200)),
        ("old_chat", 10, "User: hi\nAssistant: hello\n" * 50),
    ]
    budget = 800
    result = fit_context(blocks, budget)
    total = sum(count_tokens(r) for r in result)
    print(f"Budget: {budget} | Used: ~{total} | Blocks kept: {len(result)}")
    for i, chunk in enumerate(result):
        print(f"\n--- block {i + 1} ({count_tokens(chunk)} tokens) ---")
        print(chunk[:300] + ("…" if len(chunk) > 300 else ""))

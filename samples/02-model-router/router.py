"""
Route a developer task to local, mid, or frontier models based on metadata.
Use this pattern in scripts, CI, or a thin proxy in front of your LLM APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Tier(str, Enum):
    LOCAL = "local"       # Ollama 7–8B, zero marginal quota
    MID = "mid"           # Haiku / GPT-4o-mini / Copilot default
    FRONTIER = "frontier"  # Opus / o1 / heavy agent mode


@dataclass
class Task:
    kind: str
    files_touched: int = 1
    lines_in_context: int = 0
    needs_cross_file_reasoning: bool = False
    incident_severity: str = "low"  # low | medium | high


def route(task: Task) -> Tier:
    if task.incident_severity == "high":
        return Tier.FRONTIER

    if task.kind in {"rename", "format", "commit_message", "doc_string", "regex"}:
        return Tier.LOCAL

    if task.kind in {"single_file_fix", "test_stub", "explain_snippet"}:
        if task.lines_in_context < 400 and not task.needs_cross_file_reasoning:
            return Tier.MID
        return Tier.MID

    if task.kind in {"architecture", "security_review", "migration_plan"}:
        return Tier.FRONTIER

    if task.files_touched > 5 or task.needs_cross_file_reasoning:
        return Tier.FRONTIER

    # default: mid is the daily driver
    return Tier.MID


MODEL_MAP = {
    Tier.LOCAL: "qwen2.5-coder:7b",
    Tier.MID: "claude-sonnet-4",
    Tier.FRONTIER: "claude-opus-4",
}


if __name__ == "__main__":
    examples = [
        Task("commit_message", lines_in_context=120),
        Task("single_file_fix", lines_in_context=250),
        Task("migration_plan", files_touched=40, needs_cross_file_reasoning=True),
        Task("rename", lines_in_context=30),
    ]
    for t in examples:
        tier = route(t)
        print(f"{t.kind:20} -> {tier.value:10} ({MODEL_MAP[tier]})")

"""
Wrap LLM calls with token estimates and append to a local CSV log.
Use when the vendor UI does not give you per-request visibility.
"""

from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common_tokens import count_tokens

LOG_PATH = Path(__file__).resolve().parents[2] / "usage.csv"


def estimate_tokens(text: str) -> int:
    return count_tokens(text)


@dataclass
class UsageRecord:
    ts: str
    model: str
    input_tokens: int
    output_tokens: int
    task_label: str
    session_id: str


def log_usage(
    model: str,
    prompt: str,
    completion: str,
    task_label: str = "",
    session_id: str = "default",
) -> UsageRecord:
    record = UsageRecord(
        ts=datetime.now(timezone.utc).isoformat(),
        model=model,
        input_tokens=estimate_tokens(prompt),
        output_tokens=estimate_tokens(completion),
        task_label=task_label,
        session_id=session_id,
    )
    write_header = not LOG_PATH.exists()
    with LOG_PATH.open("a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["ts", "model", "input_tokens", "output_tokens", "task_label", "session_id"])
        w.writerow(
            [
                record.ts,
                record.model,
                record.input_tokens,
                record.output_tokens,
                record.task_label,
                record.session_id,
            ]
        )
    return record


def summarize_session(session_id: str = "default") -> dict[str, int]:
    if not LOG_PATH.exists():
        return {"input_tokens": 0, "output_tokens": 0, "calls": 0}
    inp = out = calls = 0
    with LOG_PATH.open() as f:
        for row in csv.DictReader(f):
            if row["session_id"] != session_id:
                continue
            inp += int(row["input_tokens"])
            out += int(row["output_tokens"])
            calls += 1
    return {"input_tokens": inp, "output_tokens": out, "calls": calls}


if __name__ == "__main__":
    # Simulated call
    prompt = "Summarize this diff in 5 bullets:\n" + ("+ line\n" * 80)
    completion = "- Fixed auth refresh\n- Added test\n"
    rec = log_usage("claude-sonnet-4", prompt, completion, task_label="pr_summary", session_id="demo")
    print(f"Logged: in={rec.input_tokens} out={rec.output_tokens} -> {LOG_PATH}")
    time.sleep(0.1)
    print("Session totals:", summarize_session("demo"))

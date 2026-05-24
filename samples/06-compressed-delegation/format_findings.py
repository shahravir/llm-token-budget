"""
Format code-investigation results in a compressed, cavecrew-style layout
so parent agent sessions stay small.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Finding:
    path: str
    line: int
    symbol: str
    note: str


def format_investigator(findings: list[Finding]) -> str:
    if not findings:
        return "No match."
    lines = ["Definitions / references:"]
    for f in sorted(findings, key=lambda x: (x.path, x.line)):
        lines.append(f"- {f.path}:{f.line} — `{f.symbol}` — {f.note}")
    lines.append(f"totals: {len(findings)} hits.")
    return "\n".join(lines)


def format_reviewer(path: str, line: int, severity: str, problem: str, fix: str) -> str:
    emoji = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(severity, "❓")
    return f"{path}:{line}: {emoji} {severity}: {problem}. {fix}."


if __name__ == "__main__":
    sample = [
        Finding("pkg/auth/refresh.py", 42, "refresh_token", "NPE when cookie missing"),
        Finding("pkg/auth/refresh.py", 88, "validate_session", "called without guard"),
        Finding("tests/test_refresh.py", 12, "test_refresh_ok", "no negative case"),
    ]
    print(format_investigator(sample))
    print()
    print(format_reviewer("pkg/auth/refresh.py", 42, "high", "access before null check", "guard cookie"))

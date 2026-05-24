"""
Progressive disclosure: build a lightweight repo index, load full files only when needed.
Mirrors how developers skim a tree before opening files.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path


SKIP_DIRS = {".git", "node_modules", ".venv", "dist", "build", "__pycache__"}


def build_index(root: Path, max_files: int = 200) -> str:
    lines: list[str] = [f"# Index: {root}\n"]
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = Path(dirpath).relative_to(root)
        for name in sorted(filenames):
            if count >= max_files:
                lines.append("\n…[index truncated]")
                return "\n".join(lines)
            path = rel / name
            if path.suffix == ".py":
                sigs = _python_signatures(root / path)
                lines.append(f"- `{path}` — {sigs}")
            elif path.suffix in {".ts", ".tsx", ".js", ".go", ".java"}:
                lines.append(f"- `{path}`")
            count += 1
    return "\n".join(lines)


def _python_signatures(path: Path) -> str:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError):
        return "(parse error)"
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args[:4]]
            names.append(f"def {node.name}({', '.join(args)})")
        elif isinstance(node, ast.ClassDef):
            names.append(f"class {node.name}")
        if len(names) >= 4:
            break
    return "; ".join(names) or "(empty)"


def load_files(root: Path, relative_paths: list[str], max_chars_each: int = 8000) -> str:
    parts: list[str] = []
    for rel in relative_paths:
        p = root / rel
        if not p.is_file():
            parts.append(f"\n## {rel}\n(missing)\n")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars_each:
            text = text[:max_chars_each] + "\n…[truncated]"
        parts.append(f"\n## {rel}\n```\n{text}\n```\n")
    return "".join(parts)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    index = build_index(root / "samples")
    print(index[:1500])
    print("\n--- selective load ---\n")
    print(load_files(root / "samples", ["02-model-router/router.py"])[:1200])

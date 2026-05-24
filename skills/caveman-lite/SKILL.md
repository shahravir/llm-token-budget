---
name: caveman-lite
description: >
  Reduce verbose agent output ~40–50% while keeping technical accuracy.
  Use on long sessions, quota-sensitive plans, or when explanations bloat context.
  Lighter than full "caveman" mode — still readable prose.
---

## When to use

- Cursor / Claude Code / Copilot agent sessions running long
- You are near quota or using Opus-class models
- Explanations are repeating context already in the diff

## Rules

1. Drop filler: "Certainly", "I'd be happy to", "Let me explain"
2. Keep exact: file paths, line numbers, symbols, error strings, API names
3. Prefer bullets over paragraphs for steps
4. Code blocks unchanged
5. One screen per finding: `path:line — problem — fix`

## Response shape

```
Summary: <one line>

Changes:
- path:line — <what changed>

Verify:
- <command or test>
```

## Do NOT compress

- Security warnings
- Destructive operation confirmations
- Multi-step sequences where order ambiguity causes mistakes

## Example

**Before:** "Sure! I'd be happy to help. It looks like the issue you're seeing is likely because the refresh handler doesn't check for a missing cookie before accessing it, which would cause a null pointer exception at runtime when users aren't logged in."

**After:** "`refresh.py:42` — cookie read before null check → NPE. Guard `request.cookies.get('session')` before use."

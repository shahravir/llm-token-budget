"""Token estimation with tiktoken when available; chars/4 fallback offline."""

from __future__ import annotations

_ENC = None
_USE_FALLBACK = False


def _encoding():
    global _ENC, _USE_FALLBACK
    if _USE_FALLBACK:
        return None
    if _ENC is not None:
        return _ENC
    try:
        import tiktoken

        _ENC = tiktoken.get_encoding("cl100k_base")
        return _ENC
    except Exception:
        _USE_FALLBACK = True
        return None


def count_tokens(text: str) -> int:
    enc = _encoding()
    if enc is None:
        # Rough heuristic: ~4 chars per token for English/code mix
        return max(1, len(text) // 4)
    return len(enc.encode(text))


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    enc = _encoding()
    if enc is None:
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "\n…[truncated]"

    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return enc.decode(tokens[:max_tokens]) + "\n…[truncated]"

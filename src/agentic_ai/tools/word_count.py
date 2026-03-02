"""Example tool implementations."""

from __future__ import annotations


def word_count(text: str) -> str:
    words = [w for w in text.strip().split() if w]
    return f"word_count={len(words)}"

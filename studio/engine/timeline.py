"""Narration timeline: lines, words and cue lookups.

A timeline is built either from real ElevenLabs character alignment (preferred) or from
an estimate (used only for silent animation previews, never for the final video).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", s)


@dataclass
class Word:
    text: str
    start: float
    end: float
    line: str


@dataclass
class Line:
    id: str
    text: str
    start: float
    end: float
    words: list[Word] = field(default_factory=list)


class Timeline:
    def __init__(self, lines: list[Line], total: float, estimated: bool):
        self.lines = lines
        self.by_id = {ln.id: ln for ln in lines}
        self.total = total
        self.estimated = estimated
        self.words = [w for ln in lines for w in ln.words]

    def line(self, lid: str) -> Line:
        return self.by_id[lid]

    def cue(self, lid: str, word: str | None = None, nth: int = 1, edge: str = "start") -> float:
        """Time of a word inside a line (prefix match, accent-insensitive)."""
        ln = self.by_id[lid]
        if word is None:
            return ln.start if edge == "start" else ln.end
        key = norm(word)
        seen = 0
        for w in ln.words:
            if norm(w.text).startswith(key):
                seen += 1
                if seen == nth:
                    return w.start if edge == "start" else w.end
        raise KeyError(f"cue '{word}' not found in line '{lid}': {ln.text}")

    def to_json(self):
        return {
            "total": self.total, "estimated": self.estimated,
            "lines": [{"id": ln.id, "text": ln.text, "start": ln.start, "end": ln.end,
                       "words": [[w.text, w.start, w.end] for w in ln.words]} for ln in self.lines],
        }


def words_from_alignment(text: str, chars: list[str], starts: list[float], ends: list[float]):
    """Group ElevenLabs character alignment into words (relative times)."""
    out = []
    cur, ws, we = "", None, None
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if cur:
                out.append((cur, ws, we))
            cur, ws, we = "", None, None
            continue
        if ws is None:
            ws = s
        cur += ch
        we = e
    if cur:
        out.append((cur, ws, we))
    return out


def estimate_words(text: str):
    """Rough speech timing for silent previews (Spanish, calm narrator)."""
    t = 0.0
    out = []
    for tok in text.split():
        core = re.sub(r"[^\wáéíóúñü]", "", tok.lower())
        dur = 0.09 + 0.062 * max(1, len(core))
        out.append((tok, t, t + dur))
        t += dur
        if tok.endswith((",", ";", ":")):
            t += 0.22
        elif tok.endswith((".", "?", "!", "…")):
            t += 0.38
    return out, t

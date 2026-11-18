"""Idea scoring (spec §8). A prioritisation aid, never a prediction of views."""
from __future__ import annotations

WEIGHTS = {
    "hook": 20,
    "curiosity": 15,
    "narrative": 15,
    "relevance": 15,
    "visual": 10,
    "educational": 10,
    "discussion": 10,
    "originality": 5,
}
assert sum(WEIGHTS.values()) == 100

EVIDENCE_LEVELS = ("strong", "moderate", "preliminary", "insufficient")


def weighted_score(ratings: dict[str, float]) -> float:
    """ratings: criterion -> 0..10. Returns 0..100 (rounded to 0.1). All criteria are required."""
    missing = set(WEIGHTS) - set(ratings)
    extra = set(ratings) - set(WEIGHTS)
    if missing or extra:
        raise ValueError(f"missing={sorted(missing)} extra={sorted(extra)}")
    total = 0.0
    for k, w in WEIGHTS.items():
        r = ratings[k]
        if not isinstance(r, (int, float)) or not 0 <= r <= 10:
            raise ValueError(f"rating {k} must be 0..10, got {r!r}")
        total += w * r / 10
    return round(total, 1)


def rank_ideas(ideas: list[dict]) -> list[dict]:
    """Sort by score, but push ideas without enough evidence to the bottom (editorial gate)."""
    def key(i):
        blocked = i.get("evidence") == "insufficient"
        return (blocked, -(i.get("score") or 0))
    return sorted(ideas, key=key)

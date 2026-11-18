"""Versioned JSON data store for the growth engine (studio/data/*.json).

Collections: videos, snapshots, ideas, experiments, claims, qc_reports.
Every metric value lives in a snapshot with an explicit provenance ("measured" only for numbers read
from a real source) and a source label, so dashboards can separate measured data from interpretation.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COLLECTIONS = ("videos", "snapshots", "ideas", "experiments", "claims", "qc_reports")
PROVENANCE = ("measured", "calculated", "ai_interpretation")

# Metric names follow current YouTube Studio definitions. Public views ≠ engaged views.
METRICS = ("public_views", "engaged_views", "shown_in_feed", "stayed_to_watch_pct", "swiped_away_pct",
           "avg_view_duration_s", "avg_pct_viewed", "likes", "comments", "shares", "subscribers_gained",
           "channel_subscribers", "channel_daily_views")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class StoreError(ValueError):
    pass


class Store:
    def __init__(self, root: Path | str = DATA_DIR):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- low level
    def _path(self, coll: str) -> Path:
        if coll not in COLLECTIONS:
            raise StoreError(f"unknown collection {coll!r}")
        return self.root / f"{coll}.json"

    def load(self, coll: str) -> list[dict]:
        p = self._path(coll)
        if not p.exists():
            return []
        return json.loads(p.read_text(encoding="utf-8"))

    def save(self, coll: str, rows: list[dict]) -> None:
        p = self._path(coll)
        fd, tmp = tempfile.mkstemp(dir=self.root, suffix=".tmp")   # atomic write
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, p)

    def upsert(self, coll: str, row: dict, key: str = "id") -> dict:
        """Insert or merge a row by key (idempotent)."""
        if key not in row or not row[key]:
            raise StoreError(f"{coll}: missing {key}")
        rows = self.load(coll)
        for i, r in enumerate(rows):
            if r.get(key) == row[key]:
                merged = {**r, **row, "updated_at": now_iso()}
                rows[i] = merged
                self.save(coll, rows)
                return merged
        row = {**row, "created_at": row.get("created_at", now_iso())}
        rows.append(row)
        self.save(coll, rows)
        return row

    def get(self, coll: str, id_: str, key: str = "id") -> dict | None:
        return next((r for r in self.load(coll) if r.get(key) == id_), None)

    # ---------------------------------------------------------------- snapshots
    def add_snapshot(self, video_id: str, metrics: dict[str, Any], source: str, provenance: str = "measured",
                     taken_at: str | None = None, note: str = "") -> dict:
        """Append a timestamped metric snapshot. Rejects unknown metrics and non-numeric values so nothing
        estimated can sneak in as a 'measured' number."""
        if provenance not in PROVENANCE:
            raise StoreError(f"bad provenance {provenance!r}")
        if video_id != "_channel" and not self.get("videos", video_id):
            raise StoreError(f"unknown video {video_id!r}")
        clean = {}
        for k, v in metrics.items():
            if k not in METRICS:
                raise StoreError(f"unknown metric {k!r}")
            if v is None:
                continue
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                raise StoreError(f"metric {k} must be numeric, got {v!r}")
            clean[k] = v
        if not clean:
            raise StoreError("snapshot without metrics")
        rows = self.load("snapshots")
        taken = taken_at or now_iso()
        sid = f"{video_id}@{taken}@{source}"
        snap = {"id": sid, "video_id": video_id, "taken_at": taken, "source": source, "provenance": provenance,
                "metrics": clean, "note": note}
        rows = [r for r in rows if r["id"] != sid] + [snap]   # idempotent per (video, time, source)
        self.save("snapshots", rows)
        return snap

    def snapshots_for(self, video_id: str) -> list[dict]:
        return sorted((s for s in self.load("snapshots") if s["video_id"] == video_id), key=lambda s: s["taken_at"])

    def latest_metric(self, video_id: str, metric: str) -> tuple[float, dict] | None:
        for s in reversed(self.snapshots_for(video_id)):
            if metric in s["metrics"]:
                return s["metrics"][metric], s
        return None

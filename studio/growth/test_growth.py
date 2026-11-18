"""Unit tests (stdlib unittest): python -m unittest growth.test_growth"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from growth.store import Store, StoreError
from growth.scoring import weighted_score, rank_ideas, WEIGHTS
from growth import qc


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.st = Store(self.tmp.name)
        self.st.upsert("videos", {"id": "b02", "title": "x"})

    def tearDown(self):
        self.tmp.cleanup()

    def test_upsert_is_idempotent_and_merges(self):
        self.st.upsert("videos", {"id": "b02", "format": "story"})
        rows = self.st.load("videos")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["format"], "story")
        self.assertEqual(rows[0]["title"], "x")

    def test_snapshot_requires_known_video_and_metric(self):
        with self.assertRaises(StoreError):
            self.st.add_snapshot("nope", {"public_views": 1}, "test")
        with self.assertRaises(StoreError):
            self.st.add_snapshot("b02", {"viralness": 1}, "test")

    def test_snapshot_rejects_non_numeric_and_bad_provenance(self):
        with self.assertRaises(StoreError):
            self.st.add_snapshot("b02", {"public_views": "1.3 K"}, "test")
        with self.assertRaises(StoreError):
            self.st.add_snapshot("b02", {"public_views": 1}, "test", provenance="guess")
        with self.assertRaises(StoreError):
            self.st.add_snapshot("b02", {"public_views": None}, "test")

    def test_latest_metric_and_same_snapshot_not_duplicated(self):
        self.st.add_snapshot("b02", {"public_views": 1000}, "page", taken_at="2026-11-16T00:00:00+00:00")
        self.st.add_snapshot("b02", {"public_views": 1300}, "page", taken_at="2026-11-18T00:00:00+00:00")
        self.st.add_snapshot("b02", {"public_views": 1300}, "page", taken_at="2026-11-18T00:00:00+00:00")
        self.assertEqual(len(self.st.snapshots_for("b02")), 2)
        self.assertEqual(self.st.latest_metric("b02", "public_views")[0], 1300)
        self.assertIsNone(self.st.latest_metric("b02", "stayed_to_watch_pct"))

    def test_unknown_collection(self):
        with self.assertRaises(StoreError):
            self.st.load("users")


class ScoringTests(unittest.TestCase):
    def test_weights_and_extremes(self):
        self.assertEqual(sum(WEIGHTS.values()), 100)
        self.assertEqual(weighted_score({k: 10 for k in WEIGHTS}), 100.0)
        self.assertEqual(weighted_score({k: 0 for k in WEIGHTS}), 0.0)

    def test_weighting(self):
        r = {k: 0 for k in WEIGHTS}
        r["hook"] = 10
        self.assertEqual(weighted_score(r), 20.0)

    def test_validation(self):
        with self.assertRaises(ValueError):
            weighted_score({"hook": 5})
        bad = {k: 5 for k in WEIGHTS}
        bad["hook"] = 11
        with self.assertRaises(ValueError):
            weighted_score(bad)

    def test_rank_blocks_insufficient_evidence(self):
        ideas = [{"id": "a", "score": 90, "evidence": "insufficient"}, {"id": "b", "score": 60, "evidence": "strong"}]
        self.assertEqual([i["id"] for i in rank_ideas(ideas)], ["b", "a"])


class QCTests(unittest.TestCase):
    def test_missing_file_blocks(self):
        rep = qc.run_qc("x", Path("does/not/exist.mp4"))
        self.assertFalse(rep["automated_pass"])
        self.assertEqual(rep["status"], "blocked")

    def test_manual_items_never_auto_pass(self):
        rep = qc.run_qc("x", Path("does/not/exist.mp4"))
        self.assertTrue(all(m["status"] == "pending" for m in rep["manual"]))

    def test_timeline_check(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "timeline.json"
            p.write_text(json.dumps({"estimated": False, "lines": [{"text": "Hola mundo", "words": [["Hola", 0.2, 0.5]]}]}))
            t = qc.check_timeline(p)
            self.assertEqual(t["first_word_s"], 0.2)
            self.assertFalse(t["estimated"])


class QCRenderTests(unittest.TestCase):
    """Runs against a real render if present (b04_alcohol)."""
    def test_real_render_known_findings(self):
        """b04 is technically sound except one 0.9 s near-still segment, which QC must catch."""
        studio = Path(__file__).resolve().parent.parent
        mp4 = studio / "out" / "b04_alcohol" / "b04_alcohol.mp4"
        if not mp4.exists():
            self.skipTest("render not present")
        rep = qc.run_qc("b04_alcohol", mp4)
        self.assertEqual(rep["failed"], ["no frozen picture"])
        self.assertEqual(rep["status"], "blocked")


if __name__ == "__main__":
    unittest.main()

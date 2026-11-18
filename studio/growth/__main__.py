"""Growth engine CLI.

  python -m growth qc <slug>                         technical QC of out/<slug>/<slug>.mp4 (+ saves report)
  python -m growth snapshot <video_id> <source> k=v… record measured metrics (e.g. public_views=1300)
  python -m growth idea <idea.json>                  add/update an idea; computes its weighted score
  python -m growth ideas                             ranked idea list
  python -m growth report                            per-video summary with latest measured metrics
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .store import Store
from .scoring import weighted_score, rank_ideas
from .qc import run_qc, save_report

STUDIO = Path(__file__).resolve().parent.parent


def cmd_qc(slug: str, variant: str = "") -> int:
    """variant "silent" checks the no-voice render (<slug>_sin_voz.mp4); voice-timing checks don't apply."""
    out = STUDIO / "out" / slug
    if variant == "silent":
        rep = run_qc(f"{slug}_sin_voz", out / f"{slug}_sin_voz.mp4", None)
    else:
        rep = run_qc(slug, out / f"{slug}.mp4", out / "timeline.json")
    save_report(rep)
    for c in rep["automated"]:
        print(f"  [{'OK' if c['pass'] else 'FAIL'}] {c['check']}: {c['value']} (expected {c['expected']})")
    print(f"status: {rep['status']}" + (f" — failed: {', '.join(rep['failed'])}" if rep["failed"] else ""))
    return 0 if rep["automated_pass"] else 1


def cmd_snapshot(video_id: str, source: str, pairs: list[str]) -> int:
    metrics = {}
    for p in pairs:
        k, v = p.split("=", 1)
        metrics[k] = float(v) if "." in v else int(v)
    s = Store().add_snapshot(video_id, metrics, source)
    print(json.dumps(s, ensure_ascii=False, indent=2))
    return 0


def cmd_idea(path: str) -> int:
    idea = json.loads(Path(path).read_text(encoding="utf-8"))
    idea["score"] = weighted_score(idea["ratings"])
    Store().upsert("ideas", idea)
    print(f"{idea['id']}: {idea['score']}")
    return 0


def cmd_ideas() -> int:
    for i in rank_ideas(Store().load("ideas")):
        flag = " [evidencia insuficiente]" if i.get("evidence") == "insufficient" else ""
        print(f"{i.get('score', 0):5.1f}  {i['id']:<28} {i.get('topic', '')}{flag}")
    return 0


def cmd_report() -> int:
    st = Store()
    for v in sorted(st.load("videos"), key=lambda v: v.get("published_at", "")):
        lm = st.latest_metric(v["id"], "public_views")
        views = f"{lm[0]:>6.0f} ({lm[1]['source']}, {lm[1]['taken_at'][:10]})" if lm else "     —"
        print(f"{v.get('published_at', '')[:16]:<16} {v.get('format', ''):<8} {views}  {v.get('title', '')[:60]}")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, *rest = argv
    if cmd == "qc":
        return cmd_qc(rest[0], rest[1] if len(rest) > 1 else "")
    if cmd == "snapshot":
        return cmd_snapshot(rest[0], rest[1], rest[2:])
    if cmd == "idea":
        return cmd_idea(rest[0])
    if cmd == "ideas":
        return cmd_ideas()
    if cmd == "report":
        return cmd_report()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

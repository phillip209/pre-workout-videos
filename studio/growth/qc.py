"""Automated technical QC for a rendered Short (spec §17, technical + measurable parts).

Checks: container/streams, 1080x1920, fps, duration window, full decode (no corrupt frames),
integrated loudness and true peak, long black segments, frozen segments, and timeline sanity
(hook timing, subtitle line density). Narrative/scientific quality stays a human/Claude checklist,
recorded in the same report as `manual` items so nothing is silently marked as passed.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .store import Store, now_iso

SPEC = {"width": 1080, "height": 1920, "fps": 30, "min_s": 15.0, "max_s": 60.0,
        "lufs_target": -14.0, "lufs_tol": 2.0, "peak_max_db": -0.5,
        "max_black_s": 0.5, "max_freeze_s": 0.7,   # channel standard: no still frame > 0.7 s
        "hook_first_word_max_s": 0.6}

MANUAL_ITEMS = [
    "hook understandable in the first 2 s without sound",
    "clear objective and conflict",
    "every scene adds something new",
    "payoff answers the hook",
    "character consistency across scenes",
    "subtitles readable and synced (spot-check)",
    "scientific claims match the recorded sources",
    "title/description/hashtags in Spanish, relevant, not misleading",
]


def ffmpeg_exe() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _run(args: list[str]) -> str:
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.stdout + p.stderr


def probe(path: Path) -> dict:
    """Parse ffmpeg's banner (ffprobe is not shipped with imageio-ffmpeg)."""
    out = _run([ffmpeg_exe(), "-hide_banner", "-i", str(path)])
    info: dict = {"has_video": False, "has_audio": False}
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if m:
        info["duration_s"] = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    m = re.search(r"Video: (\w+).*?, (\d+)x(\d+).*?, ([\d.]+) fps", out)
    if m:
        info.update(has_video=True, vcodec=m[1], width=int(m[2]), height=int(m[3]), fps=float(m[4]))
    m = re.search(r"Audio: (\w+).*?, (\d+) Hz", out)
    if m:
        info.update(has_audio=True, acodec=m[1], sample_rate=int(m[2]))
    return info


def analyze(path: Path) -> dict:
    """One decode pass: loudness (EBU R128 + true peak), black and frozen segments, decode errors."""
    out = _run([ffmpeg_exe(), "-hide_banner", "-v", "info", "-i", str(path),
                "-vf", "blackdetect=d=0.2:pix_th=0.06,freezedetect=n=0.002:d=0.6",
                "-af", "ebur128=peak=true", "-f", "null", "-"])
    res: dict = {}
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    if m:
        res["lufs"] = float(m[-1])
    m = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", out)
    if m:
        res["true_peak_db"] = float(m[-1])
    res["black_segments"] = [float(d) for d in re.findall(r"black_duration:([\d.]+)", out)]
    starts = [float(x) for x in re.findall(r"lavfi.freezedetect.freeze_start: ([\d.]+)", out)]
    durs = [float(d) for d in re.findall(r"lavfi.freezedetect.freeze_duration: ([\d.]+)", out)]
    res["freeze_segments"] = durs
    res["freeze_at"] = [round(a, 2) for a, d in zip(starts, durs)]
    res["decode_errors"] = len(re.findall(r"(?i)(error while decoding|corrupt|invalid data)", out))
    return res


def check_timeline(timeline_json: Path) -> dict:
    tl = json.loads(timeline_json.read_text(encoding="utf-8"))
    words = [w for ln in tl.get("lines", []) for w in ln.get("words", [])]
    first = words[0][1] if words else None
    longest = max((len(ln.get("text", "")) for ln in tl.get("lines", [])), default=0)
    return {"first_word_s": first, "lines": len(tl.get("lines", [])), "longest_line_chars": longest,
            "estimated": tl.get("estimated", False)}


def run_qc(slug: str, video: Path, timeline_json: Path | None = None) -> dict:
    checks = []

    def add(name, ok, value, expected):
        checks.append({"check": name, "pass": bool(ok), "value": value, "expected": expected})

    if not video.exists():
        add("file exists", False, str(video), "rendered MP4")
        return _report(slug, video, checks)
    info = probe(video)
    add("video stream", info["has_video"], info.get("vcodec"), "h264")
    add("audio stream", info["has_audio"], info.get("acodec"), "aac")
    add("resolution 9:16", (info.get("width"), info.get("height")) == (SPEC["width"], SPEC["height"]),
        f"{info.get('width')}x{info.get('height')}", "1080x1920")
    add("frame rate", abs(info.get("fps", 0) - SPEC["fps"]) < 0.5, info.get("fps"), f">= {SPEC['fps']}")
    d = info.get("duration_s", 0)
    add("duration", SPEC["min_s"] <= d <= SPEC["max_s"], round(d, 2), f"{SPEC['min_s']}-{SPEC['max_s']} s")
    a = analyze(video)
    add("decodes cleanly", a["decode_errors"] == 0, a["decode_errors"], 0)
    lufs = a.get("lufs")
    add("loudness", lufs is not None and abs(lufs - SPEC["lufs_target"]) <= SPEC["lufs_tol"], lufs,
        f"{SPEC['lufs_target']}±{SPEC['lufs_tol']} LUFS")
    pk = a.get("true_peak_db")
    add("true peak", pk is not None and pk <= SPEC["peak_max_db"], pk, f"<= {SPEC['peak_max_db']} dBFS")
    mb = max(a["black_segments"], default=0.0)
    add("no long black frames", mb <= SPEC["max_black_s"], mb, f"<= {SPEC['max_black_s']} s")
    mf = max(a["freeze_segments"], default=0.0)
    worst = [f"{a}s ({d:.2f}s)" for a, d in zip(a.get("freeze_at", []), a["freeze_segments"]) if d > SPEC["max_freeze_s"]]
    add("no frozen picture", mf <= SPEC["max_freeze_s"], worst or round(mf, 2), f"<= {SPEC['max_freeze_s']} s")
    if timeline_json and timeline_json.exists():
        t = check_timeline(timeline_json)
        add("real (not estimated) voice timing", not t["estimated"], t["estimated"], False)
        fw = t["first_word_s"]
        add("narration starts immediately", fw is not None and fw <= SPEC["hook_first_word_max_s"], fw,
            f"<= {SPEC['hook_first_word_max_s']} s")
    return _report(slug, video, checks)


def _report(slug, video, checks):
    failed = [c["check"] for c in checks if not c["pass"]]
    return {"id": f"{slug}@{now_iso()}", "slug": slug, "file": str(video), "created": now_iso(),
            "automated": checks, "automated_pass": not failed, "failed": failed,
            "manual": [{"item": m, "status": "pending"} for m in MANUAL_ITEMS],
            "status": "blocked" if failed else "needs_manual_review"}


def save_report(report: dict, store: Store | None = None) -> dict:
    return (store or Store()).upsert("qc_reports", report)

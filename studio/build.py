"""Build an episode: narration -> timeline -> animation -> audio mix -> MP4.

Usage (from studio/):
    run.cmd build episodes/e15_musculo_grasa            # final (requires ElevenLabs key)
    run.cmd build episodes/e15_musculo_grasa --preview  # silent preview with estimated timing
    run.cmd build episodes/e15_musculo_grasa --frames 0,3.2,10   # PNG stills for review
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from engine import FPS, SCALE, SR, W, H  # noqa: E402
from engine import audio, tts  # noqa: E402
from engine.timeline import Line, Timeline, Word, estimate_words, words_from_alignment  # noqa: E402


def ffmpeg_exe():
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def load_episode(path: Path):
    spec = importlib.util.spec_from_file_location("episode", path / "episode.py")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path))
    spec.loader.exec_module(mod)
    return mod


def build_timeline(ep, outdir: Path, preview: bool):
    lines_cfg = ep.LINES
    lead = getattr(ep, "LEAD_IN", 0.25)
    voice = np.zeros(1)
    lines = []
    t = lead
    if preview:
        for cfg in lines_cfg:
            ws, dur = estimate_words(cfg["text"])
            words = [Word(w, t + a, t + b, cfg["id"]) for (w, a, b) in ws]
            lines.append(Line(cfg["id"], cfg["text"], t, t + dur, words))
            t += dur + cfg.get("pause", 0.35)
        total = t + getattr(ep, "TAIL", 1.6)
        return Timeline(lines, total, estimated=True), np.zeros(int(total * SR))

    narr = getattr(ep, "NARRATION_FILE", None)
    if narr and (ROOT / narr).exists():
        # A finished ElevenLabs narration (e.g. generated through the ElevenLabs connector):
        # derive word timing from its pauses.
        from engine.align import align

        pcm = tts.decode_audio(ROOT / narr, ffmpeg_exe())
        words, (s0, s1), pauses, anchors = align([(c["id"], c["text"]) for c in lines_cfg], pcm)
        # optional extra silence after a line ("hold": seconds) to let a visual beat land
        for i, cfg in enumerate(lines_cfg[:-1]):
            hold = cfg.get("hold", 0.0)
            if hold <= 0:
                continue
            end = max(b for (_, a, b, lid) in words if lid == cfg["id"])
            nxt = min(a for (_, a, b, lid) in words if lid == lines_cfg[i + 1]["id"])
            cut = int(((end + nxt) / 2) * SR)
            pcm = np.concatenate([pcm[:cut], np.zeros(int(hold * SR), dtype=pcm.dtype), pcm[cut:]])
            words = [(w, a + (hold if a >= cut / SR else 0), b + (hold if a >= cut / SR else 0), lid)
                     for (w, a, b, lid) in words]
        for cfg in lines_cfg:
            ws = [Word(w, lead + a, lead + b, lid) for (w, a, b, lid) in words if lid == cfg["id"]]
            lines.append(Line(cfg["id"], cfg["text"], ws[0].start, ws[-1].end, ws))
        total = lead + len(pcm) / SR + getattr(ep, "TAIL", 1.6)
        voice = np.zeros(int((total + 1) * SR))
        audio.place(voice, pcm, lead)
        print(f"narración: {len(pcm) / SR:.1f}s, {len(pauses)} pausas, {len(anchors)} anclas")
        return Timeline(lines, total, estimated=False), voice

    if not tts.api_key():
        raise SystemExit("Falta ELEVENLABS_API_KEY. No se genera el video final sin voz real "
                         "(usa --preview para revisar solo la animación).")
    ff = ffmpeg_exe()
    vcfg = ep.VOICE
    clips = []
    for i, cfg in enumerate(lines_cfg):
        settings = {**vcfg["settings"], **cfg.get("voice", {})}
        prev_t = lines_cfg[i - 1]["text"] if i > 0 else None
        next_t = lines_cfg[i + 1]["text"] if i + 1 < len(lines_cfg) else None
        mp3, data = tts.synth_line(cfg.get("say", cfg["text"]), vcfg["voice_id"], vcfg["model"], settings,
                                   ROOT / "cache" / "tts", prev_t, next_t)
        pcm = tts.decode_audio(mp3, ff)
        al = data["alignment"]
        ws = words_from_alignment(cfg.get("say", cfg["text"]), al["characters"],
                                  al["character_start_times_seconds"], al["character_end_times_seconds"])
        # trim leading silence so the line starts on its first word
        head = max(0.0, ws[0][1] - 0.04) if ws else 0.0
        pcm = pcm[int(head * SR):]
        dur = len(pcm) / SR
        speech_end = (ws[-1][2] - head) if ws else dur
        shown = cfg["text"].split()
        if len(shown) == len(ws):  # display text may differ in spelling only
            ws = [(shown[k], a, b) for k, (_, a, b) in enumerate(ws)]
        words = [Word(w, t + a - head, t + b - head, cfg["id"]) for (w, a, b) in ws]
        lines.append(Line(cfg["id"], cfg["text"], t, t + speech_end, words))
        clips.append((t, pcm))
        t += speech_end + cfg.get("pause", 0.35)
    total = t + getattr(ep, "TAIL", 1.6)
    voice = np.zeros(int((total + 1) * SR))
    for (at, pcm) in clips:
        audio.place(voice, pcm, at)
    return Timeline(lines, total, estimated=False), voice


def mix_audio(ep, tl, voice):
    n = len(voice) if len(voice) > 1 else int((tl.total + 1) * SR)
    voice = np.resize(voice, n) if len(voice) != n else voice
    mus = audio.music(tl.total, ep.music_sections(tl), bpm=getattr(ep, "BPM", 96))[:n]
    mus = np.pad(mus, (0, max(0, n - len(mus))))
    if np.abs(voice).max() > 0:
        mus = audio.duck(mus, voice, depth=0.6)
    fx = np.zeros(n)
    for (at, name, gain) in ep.sound_cues(tl):
        audio.place(fx, audio.sfx(name), at, gain)
    # fade music out at the end
    fade = int(1.2 * SR)
    end = int(tl.total * SR)
    if end < n:
        mus[max(0, end - fade):end] *= np.linspace(1, 0, min(fade, end))
        mus[end:] = 0
    mix = voice * 1.0 + mus * 0.55 + fx * 0.5
    peak = np.abs(mix).max() + 1e-9
    return mix / peak * 0.89


def render(ep, tl, outdir: Path, wav: Path, name: str, frames_only=None):
    director = ep.make_director(tl)
    if frames_only is not None:
        for ts in frames_only:
            img = director.frame(ts)
            img.resize((W * 2, H * 2), 0).save(outdir / f"still_{ts:06.2f}.png")
        print("stills ->", outdir)
        return None
    ff = ffmpeg_exe()
    raw = outdir / f"{name}_video.mp4"
    nframes = int(tl.total * FPS)
    cmd = [ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-vf", f"scale={W * SCALE}:{H * SCALE}:flags=neighbor", "-c:v", "libx264",
           "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", str(raw)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(nframes):
        img = director.frame(i / FPS)
        proc.stdin.write(img.tobytes())
        if i % 150 == 0:
            print(f"  frame {i}/{nframes}  {time.time() - t0:.0f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    final = outdir / f"{name}.mp4"
    subprocess.run([ff, "-y", "-v", "error", "-i", str(raw), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    raw.unlink(missing_ok=True)
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--frames", default=None, help="comma separated seconds -> PNG stills")
    a = ap.parse_args()
    epdir = (ROOT / a.episode).resolve()
    ep = load_episode(epdir)
    outdir = ROOT / "out" / epdir.name
    outdir.mkdir(parents=True, exist_ok=True)
    preview = a.preview
    tl, voice = build_timeline(ep, outdir, preview)
    (outdir / ("timeline_preview.json" if preview else "timeline.json")).write_text(
        json.dumps(tl.to_json(), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"timeline: {tl.total:.1f}s ({'ESTIMADO' if tl.estimated else 'ElevenLabs'})")
    if a.frames:
        render(ep, tl, outdir, None, "", frames_only=[float(x) for x in a.frames.split(",")])
        return
    mix = mix_audio(ep, tl, voice)
    name = ep.SLUG + ("_PREVIEW_SIN_VOZ" if preview else "")
    wav = outdir / f"{name}.wav"
    audio.write_wav(wav, mix)
    final = render(ep, tl, outdir, wav, name)
    print("OK ->", final)


if __name__ == "__main__":
    main()

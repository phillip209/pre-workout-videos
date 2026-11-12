"""ElevenLabs text-to-speech with character timestamps (per line, cached).

The API key is read ONLY from the ELEVENLABS_API_KEY environment variable (user scope on
Windows is also checked). It is never written to disk or printed.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

from . import SR

API = "https://api.elevenlabs.io"


def api_key() -> str | None:
    k = os.environ.get("ELEVENLABS_API_KEY")
    if k:
        return k.strip()
    if sys.platform == "win32":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
                v, _ = winreg.QueryValueEx(h, "ELEVENLABS_API_KEY")
                return str(v).strip() or None
        except OSError:
            return None
    return None


def _req(method: str, path: str, body: dict | None = None, query: dict | None = None):
    key = api_key()
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY no está configurada.")
    url = API + path + (("?" + urllib.parse.urlencode(query)) if query else "")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")[:600]
        raise RuntimeError(f"ElevenLabs HTTP {e.code} en {path}: {msg}") from None


def list_voices():
    return _req("GET", "/v1/voices").get("voices", [])


def search_shared(language="es", accent=None, gender=None, page_size=30):
    q = {"language": language, "page_size": page_size, "sort": "usage_character_count_1y"}
    if accent:
        q["accent"] = accent
    if gender:
        q["gender"] = gender
    return _req("GET", "/v1/shared-voices", query=q).get("voices", [])


def subscription():
    return _req("GET", "/v1/user/subscription")


def decode_audio(path: Path, ffmpeg: str) -> np.ndarray:
    out = subprocess.run([ffmpeg, "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()


def synth_line(text: str, voice_id: str, model: str, settings: dict, cache: Path,
               previous_text: str | None = None, next_text: str | None = None):
    """Return (mp3_path, alignment dict). Cached by request content."""
    body = {"text": text, "model_id": model, "voice_settings": settings}
    if previous_text:
        body["previous_text"] = previous_text
    if next_text:
        body["next_text"] = next_text
    h = hashlib.sha1(json.dumps([voice_id, body], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
    cache.mkdir(parents=True, exist_ok=True)
    mp3, js = cache / f"{h}.mp3", cache / f"{h}.json"
    if mp3.exists() and js.exists():
        return mp3, json.loads(js.read_text(encoding="utf-8"))
    res = _req("POST", f"/v1/text-to-speech/{voice_id}/with-timestamps", body,
               query={"output_format": "mp3_44100_128"})
    mp3.write_bytes(base64.b64decode(res["audio_base64"]))
    align = res.get("alignment") or res.get("normalized_alignment")
    js.write_text(json.dumps({"text": text, "alignment": align}, ensure_ascii=False), encoding="utf-8")
    return mp3, {"text": text, "alignment": align}


if __name__ == "__main__":
    # python -m engine.tts voices | shared
    cmd = sys.argv[1] if len(sys.argv) > 1 else "voices"
    if cmd == "voices":
        for v in list_voices():
            lab = v.get("labels") or {}
            print(v["voice_id"], "|", v.get("name"), "|", v.get("category"), "|",
                  ", ".join(f"{k}={x}" for k, x in lab.items()))
    elif cmd == "shared":
        for v in search_shared(accent=sys.argv[2] if len(sys.argv) > 2 else None):
            print(v.get("voice_id"), "|", v.get("name"), "|", v.get("accent"), "|", v.get("gender"), "|",
                  v.get("age"), "|", v.get("use_case"), "|", (v.get("description") or "")[:80])
    elif cmd == "sub":
        s = subscription()
        print({k: s.get(k) for k in ("tier", "character_count", "character_limit", "status")})

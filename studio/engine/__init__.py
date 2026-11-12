"""PRE-WORKOUT pixel-art production engine.

Modules:
    gfx      - pixel canvas helpers, outlines, dithering, camera, transitions
    font     - original 5x7 bitmap font (uppercase + Spanish accents)
    timeline - narration timing (ElevenLabs alignment or estimate) and cues
    audio    - procedural chiptune music, sound effects, mixing/ducking
    tts      - ElevenLabs text-to-speech with timestamps (cached)
    render   - frame loop -> ffmpeg (1080x1920 MP4)
"""

W, H = 270, 480          # internal pixel canvas (scaled x4 -> 1080x1920)
SCALE = 4
FPS = 30
SR = 48000               # audio sample rate

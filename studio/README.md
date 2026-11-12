# PRE-WORKOUT Studio — producción pixel art

Sistema modular para producir Shorts verticales (1080×1920, 30 fps, MP4) con animación pixel art
programada, narración de ElevenLabs, subtítulos sincronizados por palabra, música chiptune y efectos
de sonido sintetizados. Todo el arte, la música y los sonidos se generan en código (sin material de
stock).

## Estructura

```
studio/
  build.py                 # orquesta: voz -> timeline -> animación -> mezcla -> MP4
  run.cmd                  # lanzador para Windows (usa el Python de uv y .deps/)
  engine/
    gfx.py      # lienzo 270x480 (x4), paleta, dithering, cámara, glitch, transiciones
    font.py     # fuente bitmap propia 5x7 con acentos y Ñ
    cast.py     # personajes y escenarios reutilizables (Leo, fibra muscular, adipocito, ratón, ADN, gym, lab...)
    fx.py       # partículas, humo, goteo, chispas, líneas de velocidad
    director.py # escenas, transiciones y subtítulos karaoke
    timeline.py # tiempos por palabra (ElevenLabs) y búsqueda de cues
    audio.py    # música chiptune por "mood", efectos, ducking bajo la voz
    tts.py      # ElevenLabs text-to-speech con timestamps (cacheado)
  episodes/
    e15_musculo_grasa/episode.py   # guion + escenas + diseño sonoro del piloto
  out/        # renders (ignorado por git)
  cache/      # audios de ElevenLabs cacheados (ignorado por git)
```

Cada episodio es un único `episode.py` con: `LINES` (guion por frases, con ajustes de voz por frase),
`VOICE`, `sound_cues(tl)`, `music_sections(tl)` y `make_director(tl)` (escenas). Las animaciones se
anclan a **palabras** de la narración (`tl.cue("hook", "grasa")`), así que si cambia la voz, todo
se re-sincroniza solo.

## Instalación (una vez)

```powershell
cd C:\dev\pre-workout-videos\studio
uv pip install --python "$env:APPDATA\uv\python\cpython-3.12.16-windows-x86_64-none\python.exe" --target .deps numpy pillow imageio-ffmpeg
```

(En este PC el Control de aplicaciones de Windows bloquea los ejecutables de los venv; por eso se usa
`--target .deps` con el Python de uv.)

## Voz (ElevenLabs)

**Opción A — conector de ElevenLabs en Claude (la usada en el piloto):** Claude genera la narración
completa en tu cuenta, la descarga a `episodes/<ep>/narration.mp3` y el episodio la declara en
`NARRATION_FILE`. Los tiempos por palabra se calculan con `engine/align.py` a partir de las pausas
del audio (precisión de frase). `"hold": s` en una línea añade silencio después de ella para que un
momento visual respire.

**Opción B — API directa (tiempos exactos por carácter):**

1. Configura tu clave (solo tú; nunca se guarda en el proyecto):
   `[Environment]::SetEnvironmentVariable('ELEVENLABS_API_KEY','TU_CLAVE','User')`
2. Lista voces: `.\run.cmd voices` (tus voces) o `.\run.cmd shared latin` (biblioteca, acento latino).
3. Elige la voz: `[Environment]::SetEnvironmentVariable('PW_VOICE_ID','<voice_id>','User')`
   o edita `VOICE["voice_id"]` en el episodio.

## Producir

```powershell
.\run.cmd build episodes\e15_musculo_grasa             # video final (requiere voz real)
.\run.cmd build episodes\e15_musculo_grasa --preview   # borrador SIN voz (tiempos estimados)
.\run.cmd build episodes\e15_musculo_grasa --frames 1,5.5,20   # PNG de revisión
```

Salida: `out\<episodio>\<slug>.mp4` (+ `timeline.json` con tiempos por palabra).

## Nuevo episodio

Copia `episodes/e15_musculo_grasa` a `episodes/eNN_tema`, cambia `LINES`, `TITLE`, `DESCRIPTION` y
reescribe las escenas en `make_director` reutilizando `engine.cast` y `engine.fx`.

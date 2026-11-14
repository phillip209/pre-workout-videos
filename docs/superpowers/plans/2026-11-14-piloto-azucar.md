# Piloto "¿Qué le pasa a tu cuerpo si dejas el azúcar?" — plan

> Ejecución: nativa en esta sesión (el usuario pidió "haz el piloto"). Pasos con checkbox.

**Goal:** Un Short de 30–40 s del nuevo formato, más los módulos del motor que lo hacen posible.

**Architecture:**
- Módulos nuevos `engine/hud.py` y `engine/organs.py`.
- Helpers nuevos en `engine/kit.py`: rayos X, pantalla partida, texto de impacto, número que cuenta.
- Moods de música nuevos en `engine/audio.py`.
- Episodio `episodes/b01_azucar/episode.py` con la misma interfaz que los episodios e15–e24 (LINES,
  NARRATION_FILE, sound_cues, music_sections, make_director), así `build.py` no cambia.

**Tech Stack:** Python 3.12 (uv base) + Pillow + numpy, ffmpeg de imageio-ffmpeg y ElevenLabs.

**Spec:** `docs/superpowers/specs/2026-11-14-que-le-pasa-a-tu-cuerpo-design.md`

## Global Constraints

- Lienzo 270×480, escalado ×4 a 1080×1920, 30 fps; duración 30–40 s; volumen final -14 LUFS.
- Voz: David C `qRUgOhnxGASxirG4fKjv`, `eleven_multilingual_v2`, flow `VnneuutqMxcP7Yu5Cy3X`, una toma.
- Gramática visual: verde = mejora, rojo = empeora, amarillo = transición; cada órgano tiene color fijo.
- Ningún cuadro quieto más de 0,7 s.
- Título sin la respuesta.
- Cada dato con fuente y con la población del estudio dicha.

## Datos verificados (fuentes)

| Hito | Dato | Fuente |
|---|---|---|
| Día 3 (valle) | Al dejar los refrescos 3 días: más antojos, dolor de cabeza, menos ánimo y concentración | Falbe et al., *Appetite* 2019 (25 adolescentes; preliminar) |
| Día 10 (hígado) | Niños con obesidad, azúcar cambiada por almidón 9 días: grasa en el hígado 7,2 % → 3,8 % (mediana), incluso sin bajar de peso | Schwarz et al., *Gastroenterology* 2017 |
| Día 90 (lengua) | Con menos azúcar, a los 3 meses los dulces se perciben ~40 % más dulces | Wise et al., *AJCN* 2016 |
| Giro final | Al volver al azúcar, la percepción regresó rápido a la de antes | Wise et al., *AJCN* 2016 |

## Review Focus

1. **Superposición del HUD con los subtítulos:** el HUD vive en y < 70; el texto de impacto entre y 90 y 300;
   los subtítulos en y ≥ 352.
2. **Texto de impacto que se sale del cuadro con palabras largas** ("CONCENTRACIÓN"): debe reducir la
   escala hasta caber en 250 px.
3. **El contador de días salta de 3 a 10 a 90:** la animación debe contar rápido, no teletransportarse.
4. **Legible sin sonido:** cada hito tiene su número o palabra en pantalla.
5. **Bucle:** el último cuadro empalma visualmente con el primero (mismo fondo y pose).

---

### Task 1: HUD (contador de días + barras de estado)

**Files:** Create `studio/engine/hud.py`.

**Produces:**
- `day_counter(img, day: float, max_day: int, t: float, flash: float = 0.0) -> None`: "DÍA N" grande arriba al
  centro, con barra de progreso debajo; `flash` (0–1) lo hace rebotar y cambiar de color.
- `count_day(t, keys: list[tuple[float, int]]) -> float`: interpola el día con rapidez entre fotogramas clave
  `(tiempo, día)`, con easing.
- `stat_bar(img, x, y, w, name: str, value: float, color, t, delta: float = 0.0) -> None`: barra RPG con
  nombre e ícono de flecha verde o roja según `delta`.

- [ ] Implementar.
- [ ] Verificar con un cuadro de prueba en `out/` que el contador cabe con "DÍA 90" a escala 3 y deja libre
  y ≥ 70.

### Task 2: Órganos personajes

**Files:** Create `studio/engine/organs.py`.

**Produces:**
- `brain(mood: str, t: float) -> Image`, `liver(fat: float, mood: str, t: float) -> Image` y
  `tongue(mood: str, t: float) -> Image`.
- Moods: `"happy"`, `"sad"`, `"angry"`, `"shock"` y `"pain"`.
- Colores fijos:
  - Cerebro: rosa.
  - Hígado: rojo vino, con gotas de grasa amarillas cuyo número depende de `fat`.
  - Lengua: rosa claro.
- `speech(text: str) -> Image`: globo de diálogo blanco con cola.

- [ ] Implementar.
- [ ] Verificar con una hoja con los 3 órganos × 5 moods; cada emoción se distingue a escala 2.

### Task 3: Helpers de kit (rayos X, pantalla partida, texto de impacto, número que cuenta)

**Files:** Modify `studio/engine/kit.py` (agregar al final).

**Produces:**
- `impact_text(img, text, x, y, t, t0, color, max_w=250, scale=4) -> None`: rebote con estiramiento al
  entrar, contorno grueso y escala reducida hasta caber en `max_w`.
- `count_text(start: float, end: float, t, t0, dur, fmt="{:.1f}") -> str`: número que cuenta.
- `xray(base: Image, inner: Image, cx, cy, p: float) -> Image`: lente circular que crece de radio 0 a la
  pantalla completa con `p`; borde verde de escáner.
- `split_before_after(left: Image, right: Image, p: float, labels=("DÍA 1", "DÍA 90")) -> Image`: la línea
  divisoria entra barriendo.

- [ ] Implementar.
- [ ] Verificar `impact_text` con "CONCENTRACIÓN" (no se sale del cuadro).

### Task 4: Audio — moods y sonidos nuevos

**Files:** Modify `studio/engine/audio.py`.

**Produces:**
- Moods de `music()` nuevos:
  - `"pulse"`: misterio para el gancho.
  - `"drive"`: ritmo que acelera en los escalones.
  - `"low"`: filtrado y en menor, para el valle.
  - `"triumph"`: la revelación.
- Sonidos de `sfx()` nuevos:
  - `"tick"`: contador.
  - `"scan"`: rayos X.
  - `"babble"`: voz de órgano.
  - `"bar_up"` y `"bar_down"`.

- [ ] Implementar.
- [ ] Verificar que `python -c` genera cada sonido y mood sin error y con picos ≤ 1.0.

### Task 5: Guion y narración

**Files:** Create `studio/episodes/b01_azucar/episode.py` (solo LINES y metadatos) y `narration.mp3`.

- [ ] Escribir LINES contra el mapa de retención: gancho contraintuitivo, pacto, día 3 (valle), día 10
  (hígado), día 90 (lengua), revelación, giro y pregunta de bucle.
- [ ] Generar una toma en ElevenLabs y descargarla.
- [ ] Verificar que dura 28–36 s de voz y que la alineación de `build.py --frames` no falla.

### Task 6: Escenas y render

**Files:** Modify `studio/episodes/b01_azucar/episode.py` (sound_cues, music_sections, make_director).

- [ ] Programar las escenas: gancho (Leo con dona y alarma), día 1, día 3 (cerebro con dolor y barras en
  rojo), día 10 (rayos X al hígado, que se desinfla de 7,2 % a 3,8 %), día 90 (lengua en shock con
  "+40 %"), revelación partida, giro y bucle.
- [ ] Revisar una hoja de cuadros clave con `tools_sheet.py` y corregir superposiciones.
- [ ] Render final y verificar duración, 1080×1920 y -14 LUFS.

### Task 7: Entrega

- [ ] Enviar el MP4 al usuario para aprobación. No programar en Metricool hasta que lo apruebe.

# Formato "¿Qué le pasa a tu cuerpo si…?" — diseño

Fecha: 2026-11-14 · Canal: PRE-WORKOUT (Shorts fitness en español) · Motor: `studio/` (pixel art procedural)

## 1. Intención y por qué

El canal se estanca en ~1.000–1.500 vistas por Short: YouTube los prueba con un grupo inicial y los corta.
El formato actual (mito + estudio, gym de nicho, veredicto revelado en el título) no retiene y apunta a
temas con poca demanda.

**Objetivo de negocio (del usuario):** ingresos por publicidad. Eso exige entrar al Programa de Socios
(1.000 suscriptores + 10 M de vistas de Shorts en 90 días) y luego videos que aspiren a millones de vistas
de forma repetible.

**Formato elegido (por el usuario):** "¿Qué le pasa a tu cuerpo si…?" — Leo hace algo durante un tiempo y
vemos, día a día, qué cambia dentro y fuera de su cuerpo.

**Lo que el usuario exige explícitamente:**
- Animaciones *mucho* más entretenidas.
- Guiones más estratégicos, con ganchos muy bien pensados y una estructura clara que genere retención.
- Pixel art que se entienda: que quede claro **qué** se quiere transmitir y **quién** lo transmite.
- Efectos de sonido y música que aporten interés.
- Textos en pantalla más llamativos.

## 2. Metas, no-metas, anti-metas

**Metas**
- Romper el techo de ~1.200 vistas: en los primeros 10 videos, al menos uno > 10.000 y la mediana > 3.000.
- "Se quedaron a ver" (Studio) ≥ 70 % y porcentaje medio visto ≥ 80 %.
- Que cualquiera entienda el video **sin sonido** (texto + imagen) y **sin texto** (sonido + imagen).

**No-metas (por ahora)**
- Vender productos, afiliados o cursos.
- Videos largos.
- Humor de gym y "verdadero/falso" (se descartaron o quedan para después).

**Anti-metas (sería un fracaso aunque "funcione")**
- Exagerar o inventar efectos en el cuerpo para enganchar: rompe la confianza y arriesga sanciones de
  YouTube por desinformación médica. Cada dato debe tener fuente.
- Videos que se sientan hechos en serie (misma plantilla, mismo ritmo, misma frase): YouTube puede negar la
  monetización por "contenido no auténtico / producido en serie".
- Un cuadro quieto más de ~0,7 s.

## 3. Restricciones

- **Licencia de voz:** el espacio de ElevenLabs conectado a Claude está en plan gratuito (sin licencia
  comercial). Para monetizar, la narración necesita un plan de pago en **ese** espacio. Bloquea publicar
  con monetización, no la producción.
- **Herramientas:** Windows con App Control (Python base de uv + `.deps`); ffmpeg de imageio-ffmpeg;
  ElevenLabs de a una generación; vidIQ sin créditos y canal sin autorizar (las métricas se leen en Studio).
- **Publicación:** Metricool marca 5154146, YouTube; videos alojados en GitHub raw.
- **Rigor:** fuentes revisadas por pares o de organismos de salud; describir con "puede", "en promedio" o
  "en estudios" cuando la evidencia es de grupo, no individual.

## 4. Enfoques considerados

| Enfoque | Qué es | Pros | Contras | Decisión |
|---|---|---|---|---|
| A. "¿Qué le pasa a tu cuerpo si…?" | Progresión día 1 → día 30 con cambios visibles | Curiosidad hasta el final, temas masivos (salud, peso) | Hay que sostener el rigor sin aburrir | **Elegido por el usuario** |
| B. Humor de gym en pixel art | Sketches de 10–20 s | Muy viral, bucle, etiquetas | Depende de chistes; menos suscripción | Para después |
| C. Ráfagas verdadero/falso | 7 afirmaciones en 15 s | Barato | Saturado, ganan los que dan la cara | Descartado |

## 5. Diseño del formato

### 5.1 Estructura del guion (30–40 s, mapa de retención)

| Tramo | Tiempo | Función | Regla |
|---|---|---|---|
| **Gancho** | 0–2 s | Detener el scroll | Imagen impactante desde el cuadro 1, sin intro ni logo. La frase abre una pregunta que solo se cierra al final. |
| **Pacto** | 2–5 s | Qué vamos a ver | Aparece el contador de días y la regla: "30 días sin azúcar. Vamos." |
| **Escalones** | 5–30 s | 4–5 hitos (día 1, 3, 7, 14, 30) | Cada hito dura 4–6 s y muestra **un** cambio visible + **un** número. Cada hito termina con un "re-gancho" hacia el siguiente ("pero el día 3 pasa algo raro…"). |
| **Valle** | dentro de los escalones | Tensión | Un hito donde la cosa empeora antes de mejorar (antojos, cansancio, agujetas). |
| **Revelación** | 30–36 s | Pago de la promesa | Antes / después lado a lado, con la silueta del día 1 como fantasma. Silencio de música de 0,3 s antes del golpe. |
| **Bucle** | 36–40 s | Rever y comentar | Pregunta directa ("¿Tú aguantarías el día 3?") y último cuadro que empalma con el primero. |

**Tipos de gancho** (rotar entre videos para no sonar a plantilla):
1. **Final adelantado:** mostrar el día 30 pixelado o tapado: "Así quedó Leo. Pero el día 3 casi se rinde."
2. **Contraintuitivo:** "Dejar el azúcar te va a hacer sentir peor. Al principio."
3. **Cuenta directa:** "Si caminas 30 minutos al día, en 2 semanas tu cuerpo cambia esto."
4. **Desafío al espectador:** "No vas a aguantar el día 3."

**Reglas de guion**
- Frases de 3–8 palabras. Un dato por frase.
- Hablar a "tú" (el espectador) aunque lo viva Leo.
- Prohibido revelar el resultado final antes de la revelación.
- Título sin respuesta: "¿Qué le pasa a tu cuerpo si dejas el azúcar 30 días?"

### 5.2 Quién transmite qué (claridad)

- **Narrador** (voz ElevenLabs): guía, habla al espectador, da el dato.
- **Leo:** el protagonista que vive el reto; su cuerpo y su cara muestran el efecto (energía, ánimo, forma).
- **Órganos personajes:** cerebro, hígado, corazón, intestino, músculo, célula de grasa. Cada uno con cara,
  color fijo y emociones; "hablan" con globos de texto cortos (2–4 palabras) cuando el cambio es suyo. Así
  se entiende **quién** recibe el efecto.
- **Gramática visual fija** (igual en todos los videos):
  - Verde + flecha arriba = mejora; rojo + flecha abajo = empeora; amarillo = alerta o en transición.
  - Zoom "rayos X" = entramos al cuerpo; zoom hacia afuera = volvemos a Leo.
  - Cada órgano tiene siempre el mismo color y la misma cara.

### 5.3 Sistema visual (lo que hay que programar)

- **HUD de videojuego permanente:**
  - Contador de días grande arriba, con barra de progreso hacia el día 30.
  - Barras de estado estilo RPG (p. ej. ENERGÍA, ANTOJOS, SUEÑO, GRASA, MÚSCULO), elegidas por tema, que
    suben y bajan con sonido. Se entienden al instante sin leer el subtítulo.
- **Transición rayos X:** iris o lente que entra a la zona del cuerpo afectada y muestra al órgano personaje.
- **Antes / después:** pantalla partida con silueta fantasma del día 1 y medidas que cuentan hacia arriba.
- **Calidad de animación:** anticipación y rebote (squash & stretch) en cada aparición; movimiento secundario
  (respiración, parpadeo, pelo); la cámara se mueve en cada hito; partículas en los cambios; temblor solo en
  golpes clave.
- **Textos llamativos:**
  - 1–3 palabras gigantes por golpe, con contorno grueso, rebote y color de énfasis.
  - Números que cuentan (0 → 30); la palabra clave cambia de color.
  - Subtítulos karaoke en el tercio inferior, separados del texto de impacto, que va en el centro o arriba.
- **Variedad entre videos:** fondos, momento del día y paleta según el tema; el orden de órganos y el tipo de
  gancho rotan.

### 5.4 Sonido

- Cada evento visual tiene su sonido: tic del contador, blip de barras, "zoom" de rayos X, voz de órgano tipo
  chiptune (balbuceo), golpe de revelación.
- **Música por fases:**
  - Pulso misterioso en el gancho.
  - Ritmo que acelera en los escalones.
  - Tono menor o filtrado en el valle.
  - Corte a silencio antes de la revelación.
  - Tema triunfal en la revelación, y salida que empalma con el inicio.
- La música baja automáticamente debajo de la voz; volumen final a -14 LUFS.

### 5.5 Temas iniciales (a verificar uno por uno con fuentes)

Se priorizan los de audiencia masiva y evidencia clara en una escala de días o semanas:
1. Dejar el azúcar añadido 30 días.
2. Caminar 30 minutos al día.
3. Dormir 5 horas durante una semana.
4. Dejar el alcohol 30 días.
5. Hacer sentadillas todos los días.
6. Dejar de entrenar un mes (reutiliza el material de músculo y grasa).
7. Tomar creatina a diario.
8. Pasar 10 horas sentado cada día.

Un tema se descarta si no hay evidencia suficiente para al menos 4 hitos sin inventar.

## 6. Cambios en el motor (`studio/`)

- `engine/hud.py` (nuevo): contador de días, barra de progreso, barras de estado con animación y sonido.
- `engine/organs.py` (nuevo): órganos personajes con expresiones y globos de diálogo.
- `engine/kit.py`: transición rayos X, pantalla partida antes/después, texto de impacto con rebote, números
  que cuentan.
- `engine/cast.py`: más estados para Leo (energía, cansancio, antojo, ánimo) y morfología gradual por día.
- `engine/audio.py`: música por fases con subidas, cortes y salida en bucle; sonidos nuevos (tic, rayos X,
  balbuceo de órganos).
- `episodes/b01_<tema>/`: episodios del formato nuevo, con su propia numeración.
- Plantilla de episodio con el mapa de retención como datos (hitos, tipo de gancho, re-ganchos), para que
  cada guion se escriba contra la estructura.

## 7. Proceso por video

1. Investigar el tema: fuentes y 4–5 hitos con un número cada uno.
2. Guion contra el mapa de retención, más título sin respuesta.
3. Revisión del guion: gancho en < 2 s, re-gancho en cada hito y nada revelado antes de tiempo.
4. Narración ElevenLabs (David C, `eleven_multilingual_v2`), una generación a la vez.
5. Animación, más revisión por cuadros clave (legible sin sonido y sin texto).
6. Programación en Metricool.

**Primer paso concreto:** un video piloto completo ("dejar el azúcar 30 días") para aprobar el nuevo nivel de
animación, sonido y texto antes de producir en serie.

## 8. Decisiones del usuario

- Formato A ("¿Qué le pasa a tu cuerpo si…?").
- Objetivo: ingresos por publicidad.
- Mantener el pixel art, con más entretenimiento, ganchos, estructura de retención, sonido, música, textos
  llamativos y claridad de quién transmite qué.

## 9. Decisiones mías (revisables)

- Duración 30–40 s.
- Narrador que habla a "tú", Leo como protagonista y órganos personajes con globos.
- HUD estilo videojuego como columna vertebral visual.
- Gramática de colores fija.
- Rotar 4 tipos de gancho.
- Numeración nueva `b01…`.
- Lista inicial de 8 temas.
- Metas de los primeros 10 videos.
- Piloto antes de producir en serie.
- Los posts ya programados del 15 al 17 de noviembre (formato viejo) se mantienen: sirven de comparación.
- Tras aprobar el piloto, 1 video nuevo al día a las 18:00 (Bogotá) durante la prueba de 10 videos.

## 10. Abierto para el constructor

- Paletas exactas, diseño de cada órgano y nombres de las barras por tema.
- Duración exacta de cada hito según la narración.

# Piloto B05 v2 — "¿10 minutos después de cada comida le ganan a 30 de una vez?" (sin voz)

- **Archivos:**
  - Video v2: `studio/out/b05_caminar/b05_caminar_sin_voz.mp4`
  - Video v1 (comparación): `b05_caminar_sin_voz_v1.mp4`
  - Fuente: `studio/episodes/b05_caminar/episode.py` (v1 en `out/b05_caminar/episode_v1.py` y en el historial de git)
- **Especificaciones:** 42,2 s · 1080×1920 (9:16) · 30 fps · −15,3 LUFS · pico −1,0 dBFS · subtítulos integrados.

## 1. Validación científica

| Afirmación | Fuente | Tipo | Límites |
|---|---|---|---|
| 10 min de caminata después de cada comida principal dejaron el azúcar posterior a las comidas un **12 % más bajo** que 30 min una vez al día (área bajo la curva de 3 h; razón 0,88; IC 95 % 0,78–0,99) | Reynolds AN, Mann JI, Williams S, Venn BJ. *Diabetologia* 2016;59(12):2572–2578 | Ensayo aleatorizado cruzado, 41 adultos con diabetes tipo 2, 2 semanas por plan | Población con diabetes tipo 2; corto plazo |
| Después de la cena, la reducción fue del **22 %** | Comunicado de la Universidad de Otago sobre Reynolds 2016 (citado por ScienceDaily y Healio) | Análisis secundario del mismo ensayo | Cifra del comunicado; el artículo informa el efecto principal |
| Caminar suave en pausas bajó el azúcar después de comer frente a quedarse sentado, y más que solo ponerse de pie | Buffey AJ et al. *Sports Med* 2022;52:1765–1787 | Metaanálisis de 7 estudios agudos de laboratorio | Efecto agudo; métodos heterogéneos; pausas de 2 a 30 min |
| Al contraerse, el músculo lleva GLUT4 a su superficie y absorbe más glucosa | Richter EA, Hargreaves M. *Physiol Rev* 2013;93:993–1017 | Revisión fisiológica | Mecanismo general; se simplifica como "puertas" |

**"2 minutos" eliminado.**
- La duración de las pausas en Buffey 2022 iba de 2 a 30 min. El dato de "2 min" viene de la prensa, no de una intervención única y probada.
- La v2 usa la única duración comparada directamente en un ensayo aleatorizado: 10 min después de cada comida frente a 30 min de una vez.

**El gráfico usa datos reales, no ilustrativos:**
- 30 min = 100 (referencia) y 10 min = 88, que es la razón 0,88 publicada.
- "CENA: −22 %".
- En pantalla aparecen la población, la duración, la medida (azúcar tras las comidas, 3 h) y la fuente.

## 2. Tres ganchos alternativos

1. **Elegido:** "¿Diez minutos después de cada comida… le ganan a treinta de una vez?"
   - Plantea la pregunta central y la comparación en el primer cuadro: pantalla dividida "30 MIN · 1 VEZ AL DÍA" frente a "10 MIN · TRAS CADA COMIDA" y "¿CUÁL GANA?".
2. "Leo caminó menos minutos… y su azúcar subió menos. ¿Cómo?" Es una paradoja, pero tarda más en dejar claro de qué se trata.
3. "Lo que haces justo después de comer le cambia el azúcar a tu cuerpo." Es claro pero genérico, sin tensión de comparación.

El elegido gana en claridad inmediata, en curiosidad (dos opciones, ¿cuál gana?) y en exactitud: es literalmente la comparación del estudio. Además, la pantalla dividida da una imagen fuerte.

## 3. Guion definitivo (subtítulos = narración futura)

| ID | Tiempo (ritmo de lectura) | Texto |
|---|---|---|
| hook | 0,06–4,23 | ¿Diez minutos después de cada comida… le ganan a treinta de una vez? |
| hook2 | 4,51–5,68 | Leo lo comprobó. |
| prob | 6,11–9,86 | Almuerzo grande. Después: silla, pantalla… y sueño. |
| conf | 10,14–12,88 | Ahí aparece el monstruo: el pico de azúcar. |
| turn | 13,16–15,21 | Leo se levanta y sale a caminar. |
| bio | 15,49–20,13 | Cada paso contrae sus músculos… y eso abre puertas para que entre el azúcar. |
| ev1 | 20,41–23,67 | Un estudio en adultos con diabetes tipo dos lo comparó. |
| ev2 | 23,95–28,36 | Con diez minutos tras cada comida, el azúcar fue doce por ciento más bajo. |
| ev3 | 28,74–30,45 | Tras la cena, veintidós. |
| pay | 30,73–33,97 | El monstruo se encoge… pero vuelve en cada comida. |
| disc | 34,25–37,51 | Ojo: no cura la diabetes ni reemplaza el tratamiento. |
| cta | 37,79–40,51 | Y tú, después de cenar: ¿sofá o caminata? |

- 103 palabras, a unas 2,6 palabras por segundo.
- La primera versión del guion medía 48,2 s. Se recortó y se movieron detalles a la imagen: "crece con cada bocado" se ve en vez de decirse, y "ni reemplaza el tratamiento" queda en la tarjeta.

## 4. Storyboard y dirección de animación

| # | Escena (función) | Tiempo | Imagen y acción | Cámara y transición | Sonido |
|---|---|---|---|---|---|
| 1 | Gancho (pregunta) | 0–5,9 | Pantalla dividida. A la izquierda, Leo camina al amanecer: "30 MIN · 1 VEZ AL DÍA". A la derecha, Leo camina de noche con un plato: "10 MIN · TRAS CADA COMIDA". "¿CUÁL GANA?" se ve desde el cuadro 1. Luego "LEO LO COMPROBÓ" | Zoom de 1,15× a 1× y líneas de velocidad | Impacto, golpe de aire, pitidos en "diez" y "treinta", pulso |
| 2 | Problema | 5,9–9,9 | Leo come (lleva el brazo del plato a la boca y el plato se vacía). Luego se sienta, se encorva y se duerme con "Z" flotando. Palabras de impacto: SILLA → PANTALLA → SUEÑO | Barrido lateral | Mordiscos, golpe seco, pitido, desinflado; música relajada |
| 3 | Conflicto | 10–13 | El cubo-monstruo del pico de azúcar se alza y crece de nuevo (el bocado). La barra "AZÚCAR EN SANGRE" sube. Leo, sudando, lo mira | Empuje lento y temblor al aparecer | Gruñido, barra que sube, mordisco, inflado; música en bajón |
| 4 | Giro (protagonista activo) | 13–15,3 | Leo se levanta de la silla con los brazos arriba ("¡DE PIE!") y sale caminando a la calle con un travelling. El monstruo lo sigue | Corte a travelling con capas | Golpe de aire y pasos cada 0,42 s; música con ritmo |
| 5 | Biología | 15,3–20,2 | Rayos X a la pierna. La fibra muscular se contrae al ritmo de los pasos y se abren puertas doradas GLUT4 por donde entran mini-cubos de glucosa. Textos "CONTRACCIÓN" y "PUERTAS GLUT4 · EL AZÚCAR ENTRA AL MÚSCULO" | Lente de escáner | Barrido de escáner, golpe metálico, "pop" en "puertas", destellos |
| 6 | Evidencia | 20,3–30,5 | Dos barras reales: 30 MIN = 100 (dorada) y 10 MIN = 88 (verde). Encima, "−12 %" y "CENA: −22 %". En pantalla, la población, la medida y la fuente | Iris y deriva lenta | Música de misterio, silencio y luego tema triunfal en "doce" |
| 7 | Resultado | 30,6–34 | De noche, tras la cena, Leo camina y el monstruo se encoge… y regresa guiñando junto a un plato: "VUELVE EN CADA COMIDA" | Barrido | Desinflado, gruñido, mordisco, pasos |
| 8 | Aviso | 34,2–37,6 | Tarjeta "OJO · NO CURA LA DIABETES / NI REEMPLAZA EL TRATAMIENTO / ESTUDIOS DE CORTO PLAZO". Leo, calmado | Disolución tramada y deriva | Alarma suave y golpe seco |
| 9 | Pregunta y bucle | 37,7–42,2 | La misma composición dividida del cuadro 1: a la izquierda Leo en el SOFÁ, a la derecha Leo en CAMINATA. "¿SOFÁ O CAMINATA?" | Pixelado | "Pop" y "ding" |

## 5. Comportamiento de los personajes

- **Leo:** siempre hace algo. Camina, come, se sienta, se duerme, se levanta, sale a la calle, vuelve a caminar de noche y mira al monstruo. Respira y parpadea en todas las escenas.
- **El monstruo del pico de azúcar (cubo de azúcar):**
  - Representa la subida de azúcar después de comer.
  - Aparece tras el almuerzo, crece con el bocado y sigue a Leo por la calle.
  - Se encoge cuando Leo camina y vuelve en cada comida.
  - Su regreso es lo que justifica el hábito, no una victoria única.
- **Fibra muscular:** se contrae al ritmo de los pasos. Las puertas GLUT4 se abren más en cada contracción y la glucosa entra desde fuera hacia la fibra.

## 6. Dirección de voz (para cuando haya créditos)

- **Voz:** David C, modelo multilingüe, una sola toma, aceleración ×1,05–1,10 si hace falta para quedar en unos 40 s.
- **Tono por escena:**
  - Pregunta inicial con curiosidad, subiendo al final.
  - "Leo lo comprobó" con complicidad.
  - Problema con desgano.
  - Monstruo con tensión.
  - Giro con energía.
  - Biología clara y explicativa.
  - Pausa antes de "doce por ciento".
  - Aviso serio y breve.
  - Pregunta final conversacional.
- **Antes de grabar:** los tiempos de este documento son de lectura. Con la voz real, el alineador vuelve a sincronizar todo.

## 7. Control de calidad

- **Automático:** todo correcto (`studio/data/qc_reports.json`):
  - Stream de video y de audio.
  - 1080×1920, 30 fps, 42,2 s.
  - Decodificación limpia.
  - −15,3 LUFS, pico −1,0 dBFS.
  - Sin pantallas negras y 0,0 s de imagen congelada.
- **Revisión manual:**
  - Hecha: pregunta legible en el cuadro 1, aviso conservado, bucle (el último cuadro repite la composición del primero), fuentes en pantalla y gráfico con datos reales.
  - Pendientes de validar en el celular:
    - Legibilidad de los textos pequeños (población y fuente, escala 1).
    - Ritmo de lectura de los subtítulos.
- **Limitación conocida:** Leo "sentado" está de pie delante de la silla, porque el personaje no tiene pose sentada. Se puede añadir esa pose en el motor.

## 8. Comparación v1 → v2

| Aspecto | v1 | v2 | Por qué |
|---|---|---|---|
| Gancho | "Dos minutos caminando después de comer… y su pico de azúcar fue más bajo." Resultado primero, sin pregunta | "¿Diez minutos después de cada comida le ganan a treinta de una vez?" Pregunta comparativa con "¿CUÁL GANA?" en el cuadro 1 | Requisito de plantear la pregunta central en 2 s; comparación concreta |
| Duración citada | "2 minutos" | 10 min frente a 30 min (Reynolds 2016) | "2 min" no estaba respaldado como intervención única |
| Protagonista | De pie quieto en 5 de 9 escenas | Come, se duerme, se levanta, camina de día y de noche | Requisito de protagonista activo |
| Monstruo | Aparecía, seguía y se encogía, sin consecuencia | Crece con el bocado, persigue a Leo, se encoge y vuelve en cada comida (motiva el hábito) | Función narrativa clara |
| Biología | Fibra estática con cubos que flotaban | La fibra se contrae al ritmo de los pasos y abre puertas GLUT4 por donde entra la glucosa | Mecanismo correcto y visible (Richter y Hargreaves 2013) |
| Gráfico | Dos curvas ilustrativas sin valores | Dos barras con los valores reales (100/88), −12 %, cena −22 %, población, medida y fuente | Datos reales e identificables |
| Contador superior | "TRAS COMER" fijo en todo el video | Eliminado; cada escena da su propio contexto | Ruido visual sin función |
| Transiciones | Cortes entre escenas sin conexión | Comida → silla → monstruo → levantarse → calle → rayos X de la pierna en movimiento → datos → caminata nocturna → aviso → bucle | Continuidad de causa y efecto |
| Aviso | Breve, entre otros textos | Tarjeta propia, legible y con tres líneas | Conservar y destacar |
| Pregunta final | "¿Cuántos minutos caminas tú después de comer?" | "Y tú, después de cenar: ¿sofá o caminata?" | Respuesta binaria, fácil de comentar, que conecta con la cena (−22 %) |
| Duración | 39,8 s | 42,2 s (guion recortado desde 48,2 s) | Tiempo suficiente para un dato verificado y su contexto |

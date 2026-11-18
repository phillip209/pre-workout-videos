# B05C — "Caminar después de comer" · formato Leo Cristal (piloto sin voz)

**Archivos**
- Video: `studio/out/b05c_cristal/b05c_cristal_sin_voz.mp4`
- Código: `studio/engine/crystal/` y `studio/episodes/b05c_cristal/episode.py`
- Personaje: `docs/personaje/leo_cristal_referencia.png` y `leo_cristal_capas.png`

## 1. Auditoría técnica (antes de construir)

- **Pipeline existente:** `build.py` → narración y línea de tiempo → `Director` (lienzo de 270×480 escalado ×4) → mezcla numpy → ffmpeg. Motor pixel art en `engine/` (gfx, cast, kit, story).
- **Dependencias disponibles:** Python 3.12 (uv), Pillow, numpy, ffmpeg (imageio). Fuentes del sistema: Segoe UI y Bahnschrift.
- **No disponible** (verificado el 2026-11-18):
  - Blender u otro motor 3D.
  - GPU dedicada (no hay `nvidia-smi`).
  - Herramientas de generación de imagen o video conectadas: ElevenLabs conectado solo hace voz y vidIQ tiene 0 créditos.
  - Windows App Control bloquea los ejecutables de los entornos virtuales.
- **Decisión:** el 3D real y el fotorrealismo de las referencias no son viables aquí. Se construyó el mejor sustituto posible: un **motor 2.5D vectorial nativo a 1080×1920** (`engine/crystal/`) con estos componentes:
  - **Personaje articulado (rig)** con poses parametrizadas: caminar, sentarse, comer, levantarse y mirar, más 6 expresiones. No es una imagen fija que se mueve con paneos.
  - **Capas anatómicas separadas:** cuerpo de vidrio, órganos que solo se encienden cuando se explican, músculos y esqueleto.
  - **Materiales de vidrio** (transparencia, borde frío, reflejos) y brillo difuso (*bloom*).
  - **Cámara cinematográfica:** dolly, grúa, seguimiento, primer plano y tomas macro.
  - **Profundidad de campo:** fondos pintados y desenfocados con paralaje.
  - **Transiciones narrativas:**
    - "Inmersión": la cámara entra al abdomen o a la pierna y el siguiente mundo se abre desde ese punto.
    - "Puente de partícula": una molécula de glucosa se enciende y se convierte en la siguiente toma.
  - **Corrección de color tipo cine** (viñeta y grano) y **subtítulos tipográficos** con palabra clave resaltada.
- **Compatibilidad:** el motor pixel art sigue intacto. `build.py` admite episodios nativos (`NATIVE = True`) y el modo sin voz (`--silent`).

## 2. Personaje oficial — Leo Cristal

| Elemento | Especificación |
|---|---|
| Cuerpo | Vidrio transparente con borde gris azulado y brillo especular arriba a la izquierda |
| Esqueleto | Color hueso con volumen en 3 tonos: cráneo, mandíbula articulada, costillas, esternón, clavículas, columna, pelvis, fémures, tibia y peroné, manos y pies |
| Rasgos fijos | Ojos grandes redondos con iris ámbar, cinta roja con "PW" (firma del canal), cabeza grande |
| Expresiones | Neutral, curioso (una ceja arriba), sorprendido (ojos grandes y mandíbula abierta), contento (ojos sonrientes), cansado (párpados caídos), molestia (ceño). Como un cráneo no tiene labios, la emoción se transmite con párpados, cejas óseas, tamaño de pupila y mandíbula. |
| Color = información | Naranja: digestión y glucosa · rojo: sangre · violeta: "puertas" GLUT4 · azul: músculo en reposo · naranja-rojo: músculo trabajando. Solo se ilumina lo que se explica. |
| Originalidad | Mismo género que las referencias (esqueleto en cuerpo transparente), con identidad propia. No usa la cinta morada "MI" ni marcas comerciales. |

## 3. Guion final validado (español) y tiempos

Tiempos a ritmo de lectura (`--silent`). Con la voz real, el alineador vuelve a sincronizar todo.

| ID | Tiempo | Narración |
|---|---|---|
| hook | 0,10–4,81 | ¿Sabías que caminar después de comer puede cambiar lo que pasa dentro de tu cuerpo? |
| prob | 5,09–8,91 | Después de comer, la glucosa de los alimentos pasa a la sangre. |
| contra | 9,19–12,89 | Pero si te quedas sentado, tus músculos están casi en reposo. |
| mech | 13,17–19,40 | Cuando caminas, tus músculos se contraen… y pueden captar glucosa de la sangre para usarla como energía. |
| reveal | 19,68–25,40 | Por eso, varios estudios han visto que caminar después de comer puede reducir la subida de glucosa. |
| pay | 25,68–29,90 | No hace falta entrenar fuerte: una caminata ligera es un buen comienzo. |
| disc | 30,18–33,61 | Eso sí: no cura la diabetes ni reemplaza un tratamiento. |
| cta | 33,89–37,08 | ¿Tú caminas después de comer… o te quedas sentado? |

- **Total:** 38,9 s, con 107 palabras.
- **Dirección de voz:** David C, conversacional.
  - Curiosidad en la pregunta inicial.
  - Explicativa en el problema.
  - Un poco más baja en el contraste.
  - Con energía en el mecanismo.
  - Breve silencio antes de la revelación.
  - Cálida en el resultado.
  - Sobria en el aviso.
  - La pregunta final, directa a la cámara.

## 4. Storyboard (cada toma: qué pasa · qué entiende el espectador · evento visual · qué hace Leo · cámara · qué cambia · qué genera curiosidad)

1. **Gancho, en la mesa (0–5 s)**
   - Primer plano extremo del plato con vapor y tintineo de cubiertos.
   - La cámara sube en grúa hasta Leo, que mastica con el tenedor y la mandíbula en movimiento.
   - En "caminar" empuja la silla y se levanta. En "dentro" el estómago se ilumina en naranja.
   - Curiosidad: ¿qué pasa dentro?
2. **Problema, inmersión (5–9 s)**
   - La cámara entra por el abdomen y aparece el intestino: trozos de comida avanzan, se descomponen en glucosa (hexágonos dorados) y cruzan hacia un capilar.
   - Un puente de partícula lleva al **torrente sanguíneo en primera persona**, con anillos que pasan hacia la cámara.
   - La glucosa aumenta y un indicador sube.
3. **Contraste, en el sofá (9–13 s)**
   - Leo, sentado y cansado bajo la luz del televisor.
   - Dolly hacia sus piernas: "MÚSCULOS EN REPOSO".
   - Inmersión en el músculo en reposo (fibras azules): las puertas están cerradas y **la glucosa pasa de largo**.
   - Curiosidad: ¿y si se mueve?
4. **Mecanismo, en el parque (13–19,4 s)**
   - Leo camina hacia la cámara, que retrocede y luego baja hasta las piernas. Los músculos se encienden con cada paso.
   - Inmersión en el músculo activo: las fibras se contraen al ritmo de los pasos y las **puertas GLUT4 se abren**.
   - **Solo parte** de la glucosa entra y destella como energía; el resto sigue por el capilar. No se representa que caminar elimine toda la glucosa.
5. **Revelación (19,7–25,4 s)**
   - Un puente de partícula lleva a la visualización: dos curvas **marcadas como ILUSTRATIVO** ("Sentado" frente a "Caminando") y la fuente.
   - Corte a Leo caminando, que reacciona primero sorprendido y luego contento.
6. **Resultado (25,7–29,9 s)**
   - Plano amplio cinematográfico del parque al atardecer: faroles que se acercan, hojas que caen y la cámara que se aleja.
   - Leo camina relajado: "CAMINATA LIGERA".
7. **Aviso (30,2–33,6 s)**
   - Plano medio. Leo baja el ritmo y aparece una tarjeta: "No cura la diabetes / ni reemplaza un tratamiento médico".
8. **Final (33,9–39 s)**
   - Regreso a la mesa con el plato en primer plano (bucle con el cuadro 1).
   - Primer plano de Leo mirando a la cámara, curioso y luego contento: "¿Tú caminas después de comer… o te quedas sentado?".

## 5. Ciencia

| Afirmación en el video | Fuente | Nota |
|---|---|---|
| La glucosa de los alimentos pasa a la sangre | Fisiología básica | Se simplifica en la animación del intestino |
| Al contraerse, el músculo capta glucosa de la sangre | Richter y Hargreaves, *Physiol Rev*, 2013 (GLUT4) | Representado como "puertas" |
| Caminar después de comer puede reducir la subida de glucosa | Buffey et al., *Sports Med*, 2022 (metaanálisis de 7 estudios de laboratorio) · Reynolds et al., *Diabetologia*, 2016 (ensayo aleatorizado, 41 adultos con diabetes tipo 2) | Efectos agudos o de corto plazo |
| Curvas | — | **Ilustrativas**, así se indica en pantalla. No muestran datos de ningún estudio |

- No se usa ninguna duración concreta.
- "2 minutos" sigue descartado.

## 6. Comparación con B05 pixel (v2)

| | B05 pixel v2 | B05C Leo Cristal |
|---|---|---|
| Estilo | Pixel art de 270×480 escalado | Vectorial nativo de 1080×1920, vidrio, bloom, profundidad de campo y corrección de color |
| Personaje | Leo pixel; la anatomía aparece en escenas separadas | La anatomía está dentro del propio personaje y se ilumina según la historia |
| Viaje dentro del cuerpo | Rayos X con un lente circular | Inmersión real: abdomen → intestino → sangre en primera persona → músculo |
| Variedad de planos | Plano medio en casi todas las tomas | Primer plano extremo, grúa, plano medio, dolly a las piernas, macro, primera persona, plano amplio y primer plano final |
| Dato | Real (Reynolds −12 % / −22 %) | Cualitativo con curvas ilustrativas, según la nueva directiva. Se pierde el dato numérico concreto, que era más fuerte para la credibilidad |
| Música | Chiptune | Pads y punteos suaves de estilo cinematográfico |

## 7. Limitaciones reales

- **No es 3D ni fotorrealista.** El acabado es de ilustración vectorial con materiales simulados. Las referencias (renders 3D) requieren Blender con una GPU o un generador de video con IA.
- **Vista frontal en todas las tomas:** el personaje no tiene vista lateral ni giros de cámara alrededor de él. "Caminar" es hacia la cámara.
- **Interacción simplificada:** en el sofá, Leo está sentado de frente con el sofá dibujado alrededor, sin contacto físico real con los cojines.
- **Rendimiento:** unos 0,9 s por cuadro (alrededor de 17 min por video) en este equipo.

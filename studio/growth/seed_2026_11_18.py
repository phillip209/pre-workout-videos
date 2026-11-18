"""One-off seed: register published Shorts and the measurements available on 2026-11-18.

Sources:
- YouTube public channel page (Shorts tab), read 2026-11-18 ~22:00 UTC. YouTube rounds to 0.1 K above
  1,000 views, so those values carry ±50 precision (noted on each snapshot).
- Metricool channel evolution (YTEV01 subscribers, YTEV02 daily views).
Run once:  python -m growth.seed_2026_11_18
"""
from __future__ import annotations

from .store import Store

T = "2026-11-18T22:00:00+00:00"

# (youtube_id, slug, title, published_local, format, series, public_views)
VIDEOS = [
    ("LGc3wXI1H9k", "v01_descanso", "¿Descansas solo 30 segundos entre series…?", "2026-10-20T00:33", "legacy", None, 105),
    ("EmnAhg3krAY", "v02_ayunas", "¿Entrenar en ayunas quema más grasa?", "2026-11-04T16:04", "legacy", "mitos", 53),
    ("Pg6dvTXEW00", "v03_proteina30g", "¿Solo absorbes 30 g de proteína por comida? MITO", "2026-11-05T16:03", "legacy", "mitos", 1000),
    ("l-5o7ezihXs", "v04_agujetas", "¿Sin agujetas no creció el músculo? ENGAÑOSO", "2026-11-06T16:03", "legacy", "mitos", 1100),
    ("MnRXIWJDTcc", "v05_abdominales", "¿Los abdominales queman la grasa de la barriga? HUMO", "2026-11-07T16:02", "legacy", "mitos", 1100),
    ("XlEoiJ2MIUE", "v06_ventana", "¿Hay solo 30 minutos para tomar proteína? PARCIALMENTE CIERTO", "2026-11-08T16:03", "legacy", "mitos", 1100),
    ("XXxMbUEWQfs", "v07_creatina", "¿La creatina daña los riñones? VERDAD", "2026-11-09T16:02", "legacy", "mitos", 491),
    ("uGL5MQ9TmTg", "v08_pesado", "¿Hay que levantar pesado para ganar músculo? MITO", "2026-11-10T16:02", "legacy", "mitos", 777),
    ("K6S5ZDkhZUY", "v09_sentadilla", "¿La sentadilla profunda arruina las rodillas? MITO", "2026-11-11T16:01", "legacy", "mitos", 1200),
    ("pgrh8pHPo9U", "v10_estirar", "¿Estirar antes de entrenar evita lesiones? MITO", "2026-11-12T16:02", "legacy", "mitos", 1000),
    ("futKPfpjDuU", "e15_musculo_grasa", "¿Si dejas el gym, tu músculo se convierte en grasa? MITO", "2026-11-13T16:00", "pixel_myth", "mitos", 1600),
    ("nQUHPj8xJJw", "e20_musculo_pesa", "¿El músculo pesa más que la grasa? ENGAÑOSO", "2026-11-13T18:00", "pixel_myth", "mitos", 1200),
    ("Kibg3JxXT88", "e16_pasos", "¿Necesitas 10 000 pasos al día? PARCIALMENTE CIERTO", "2026-11-14T16:00", "pixel_myth", "mitos", 1200),
    ("sxaTYbO0NQY", "e21_agujetas", "¿Las agujetas son culpa del ácido láctico? MITO", "2026-11-14T18:00", "pixel_myth", "mitos", 1200),
    ("RIPnIYnvNgw", "b01v2_azucar", "90 días sin azúcar: lo más raro le pasó a su lengua", "2026-11-14T20:00", "pixel_story", "experimentos", 1200),
    ("ybhf5j5ux6E", "b02_dormir", "Durmió 4 horas dos noches: lo más raro fue su hambre", "2026-11-15T16:00", "pixel_story", "experimentos", 1300),
    ("s7HMFUuWdyw", "b03_cafe", "Café a las 4 de la tarde: lo más raro es que no notó nada", "2026-11-15T18:00", "pixel_story", "experimentos", 1300),
    ("mtCyTMzymyA", "b04_alcohol", "Un mes sin alcohol: lo más raro fue su análisis de sangre", "2026-11-16T16:00", "pixel_story", "experimentos", 1300),
    ("8Z8XkgNLleU", "e23_ninos_pesas", "¿Las pesas frenan el crecimiento de los niños? MITO", "2026-11-16T18:00", "pixel_myth", "mitos", 1100),
    ("p4fowEQh8Gk", "e19_cafeina", "¿La cafeína mejora el rendimiento deportivo? VERDAD", "2026-11-17T16:00", "pixel_myth", "mitos", 1200),
    ("dnybY1-7H4Q", "e24_proteina", "¿Más proteína = más músculo sin límite? MITO", "2026-11-17T18:00", "pixel_myth", "mitos", 1000),
]

# Metricool YTEV01/YTEV02 daily rows (Bogotá dates); later days not yet reported by Metricool.
CHANNEL = [("2026-11-13", 13, 2715), ("2026-11-14", 16, 3811), ("2026-11-15", 20, 2745),
           ("2026-11-16", 23, None), ("2026-11-17", 26, None), ("2026-11-18", 26, None)]

NOTES = {
    "b02_dormir": "Post edited outside the session on 2026-11-15 13:33: added unrelated hashtags "
                  "#peliculas #series #parati #fyp #foryou #foryoupage.",
    "b02_dormir_qc": "QC: near-frozen picture 0.90 s at 23.77 s (standard 0.7 s).",
    "b04_alcohol_qc": "QC: near-frozen picture 0.90 s at 27.07 s (standard 0.7 s).",
}


def main():
    st = Store()
    for yid, slug, title, pub, fmt, series, views in VIDEOS:
        st.upsert("videos", {"id": slug, "youtube_id": yid, "title": title, "published_at": pub + "-05:00",
                             "format": fmt, "series": series, "language": "es",
                             "url": f"https://www.youtube.com/shorts/{yid}",
                             "notes": [n for k, n in NOTES.items() if k.startswith(slug)]})
        st.add_snapshot(slug, {"public_views": views}, "youtube_public_page", taken_at=T,
                        note="Public count; YouTube rounds ≥1000 to 0.1 K." if views >= 1000 else "Public count.")
    for day, subs, views in CHANNEL:
        st.add_snapshot("_channel", {"channel_subscribers": subs, "channel_daily_views": views},
                        "metricool_ytev", taken_at=f"{day}T23:59:00-05:00")
    print(f"seeded {len(VIDEOS)} videos")


if __name__ == "__main__":
    main()

"""Snapshot of YouTube Studio metrics read on 2026-11-18 ~19:20 UTC (period: since publication).

Read by Claude in the user's signed-in Chrome (Studio > Analytics > Overview / Engagement), read-only.
Views are shown rounded by Studio above 1,000 (e.g. "1,3 K"); engaged views, %, durations and likes are
exact as displayed. e24 was < 24 h old at read time.
Run once:  python -m growth.seed_studio_2026_11_18
"""
from __future__ import annotations

from .store import Store

T = "2026-11-18T19:20:00+00:00"
SRC = "youtube_studio"

ROWS = {
    # slug: public_views, engaged_views, stayed_to_watch_pct, avg_pct_viewed, avg_view_duration_s, likes, subscribers_gained
    "b01v2_azucar": (1200, 769, 62.0, 68, 30, 26, 1),
    "b02_dormir": (1300, 848, 57.3, 67, 29, 24, 1),
    "b03_cafe": (1300, 845, 62.0, 66, 29, 31, 5),
    "b04_alcohol": (1300, 747, 58.9, 54, 21, 12, 1),
    "e15_musculo_grasa": (1600, 1000, 66.4, 49, 28, 38, 1),
    "e20_musculo_pesa": (1200, 786, 61.5, 54, 21, 19, 3),
    "e24_proteina": (1000, None, 63.6, None, None, 28, 0),
    "v09_sentadilla": (1200, 519, 39.3, 42, 17, 5, 1),
    "v03_proteina30g": (1000, None, 32.0, None, None, 8, 2),
}
KEYS = ("public_views", "engaged_views", "stayed_to_watch_pct", "avg_pct_viewed", "avg_view_duration_s", "likes",
        "subscribers_gained")


def main():
    st = Store()
    for slug, vals in ROWS.items():
        st.add_snapshot(slug, dict(zip(KEYS, vals)), SRC, taken_at=T,
                        note="Studio, since publication. public_views rounded by Studio (0.1 K).")
    # channel, last 28 days (Oct 21 - Nov 17)
    st.add_snapshot("_channel", {"public_views": 22500, "engaged_views": 11200, "stayed_to_watch_pct": 48.9,
                                 "likes": 347, "subscribers_gained": 23}, SRC, taken_at=T,
                    note="Channel, last 28 days. Shorts traffic: Shorts feed 96.6 %, search 1.8 %, channel pages 0.8 %. "
                         "Monthly audience 2.5 K, 99 % new viewers.")
    print(f"stored {len(ROWS)} Studio snapshots")


if __name__ == "__main__":
    main()

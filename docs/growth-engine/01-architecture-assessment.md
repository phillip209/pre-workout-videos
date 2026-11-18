# YouTube Shorts Growth Engine — architecture assessment and staged plan

Date: 2026-11-18 · Scope: `C:\dev\pre-workout-videos` (branch `feat/pixel-art-studio`).
Internal document in English; all public-facing output stays in Latin American Spanish.

## 1. What actually exists today (inspected)

| Area | Implementation | Status |
|---|---|---|
| Rendering pipeline | `studio/build.py`: narration -> word timeline -> per-frame Pillow drawing (270×480, ×4 nearest) -> numpy audio mix -> ffmpeg (libx264, AAC, loudnorm −14 LUFS) | Working, tested on 15+ episodes |
| Animation engine | `studio/engine/`: `gfx` (camera, transitions, glitch), `font` (own 5×7 font with accents), `cast`, `cast_plus` (Leo close-up, the Craving monster, sweets aisle, VHS rewind, gauge), `cast_villains` (villain family, organs, backgrounds), `organs`, `hud` (day counter, RPG bars), `fx`, `kit` (impact text, x-ray, split, counters) | Working |
| Story template | `studio/engine/story.py`: reusable builders for hook close-up, context, villain rise, x-ray, inner metric, lurk, slow-mo, reveal, twist+loop | Working (used by b02–b04) |
| Subtitles | `engine/director.py`: karaoke subtitles, per-word emphasis colours | Working |
| Voice | ElevenLabs via Claude connector (one take per episode, downloaded, sped up with atempo) or direct API (`engine/tts.py`, needs `ELEVENLABS_API_KEY`) | Connector workspace out of credits (quota 10,000/month); API key not set |
| Word timing | `engine/align.py`: pause detection + segmental DP over punctuation | Working (phrase-level precision) |
| Sound | `engine/audio.py`: synthesized chiptune by phase (pulse, drive, low, mystery, silence, triumph…), ~30 synthesized SFX, ducking | Working |
| Episodes | `studio/episodes/<slug>/episode.py` (LINES, NARRATION_FILE, TITLE, DESCRIPTION, TAGS, sound_cues, music_sections, make_director) | 15 episodes |
| Review | `tools_sheet.py` + ad-hoc contact sheets; frame strips via ffmpeg | Manual, not persisted |
| Publishing | Metricool connector (brand 5154146) via Claude; media hosted on GitHub raw URLs | Working, manual through Claude |
| Analytics | Metricool channel evolution (daily views/subs, ~2-day lag); YouTube public page (rounded views); vidIQ (0 credits until 2026-12-03; channel not authorized → no Studio metrics) | **No access to stayed-to-watch, retention, traffic sources** |
| Research | vidIQ (no credits), web search | Ad hoc, not persisted |
| Data store, experiments, idea DB, QC reports, dashboard | — | **Missing** |

There is no backend service, database, agent framework or UI in this repo: it is a Python CLI
production tool driven by Claude sessions. "Agents" today are Claude itself following the documented
workflow. The architecture below keeps that shape (no microservices) and adds a persistent,
inspectable data layer plus deterministic tools.

## 2. Real performance data (2026-11-18, public page + Metricool)

| Video (publication) | Format | Public views |
|---|---|---|
| e15 músculo → grasa (11-13 16:00) | myth, pixel v1 | 1.6 K |
| e20, e16, e21 (11-13/14) | myth | 1.2 K each |
| **b01v2 90 días sin azúcar (11-14 20:00)** | new story format | **1.2 K** |
| **b02 dormir 4 h (11-15 16:00)** | new story format | **1.3 K** |
| **b03 café 4 PM (11-15 18:00)** | new story format | **1.3 K** |
| **b04 un mes sin alcohol (11-16 16:00)** | new story format | **1.3 K** |
| e23, e19, e24 (11-16/17) | myth (old format) | 1.0–1.2 K |

Subscribers: 11 (11-13) → 26 (11-18). Daily channel views (Metricool): 2.7 K (11-13), 3.8 K (11-14),
2.7 K (11-15); later days not yet reported.

**Observation (fact):** the four new-format videos landed in the same 1.2–1.3 K band as the old format.
The plateau is remarkably uniform across very different topics, formats and quality levels (only two
outliers below it: 53 and 491 views, the earliest uploads).

**Hypotheses (not verified):**
1. The audience test pool is limited by channel-level signals, not by individual creative quality.
2. A shared publishing factor affects every upload: all go through Metricool's API with
   `isAiGeneratedContent=true` (YouTube "altered or synthetic content" label).
3. Viewers swipe in the first seconds in every format (would show as low "stayed to watch").
4. Topic/audience mismatch: the feed tests the videos with audiences that do not care about the niche.

None of these can be confirmed without YouTube Studio data (stayed-to-watch, average % viewed,
traffic sources, retention curve). **This is the single most important missing dependency.**

**Metadata issue found:** the b02 post was edited on 2026-11-15 13:33 (outside this session) and now
ends with `#peliculas #series #parati #fyp #foryou #foryoupage`. These are unrelated to the content;
YouTube's spam policy covers misleading metadata, and they can send the video to the wrong test
audience. Recommend removing them.

## 3. Gap analysis vs. the specification

| Spec module | Reuse | Missing |
|---|---|---|
| Rendering, animation, characters, sound, subtitles | Engine above | Character spec sheets as data |
| Hook/script/storyboard engines | Template b01v2 + `story.py` | Structured idea/hook/scene records and validation |
| Fact-checking | Done manually per episode docstring | Structured claim registry with sources and limits |
| Video QC | Manual frame review | Automated technical QC + persisted report per render |
| Analytics integration | Metricool evolution, public page | Studio metrics (needs authorization), timestamped snapshots per video |
| Experiments | — | Experiment registry, controlled variables |
| Idea DB + scoring | — | Idea store + weighted score (spec §8) |
| Dashboard | — | Read-only HTML dashboard over the data store |
| Publishing | Metricool via Claude | Traceability record (episode ↔ render ↔ post ↔ YouTube id) |

## 4. Architecture decision

- Add a `studio/growth/` Python package and a versioned JSON data store in `studio/data/`
  (plain files: diffable in git, no server, works under Windows App Control).
- Every record carries `provenance` (`measured` / `calculated` / `ai_interpretation`) and a `source`.
  Metrics are stored only when measured; nothing is estimated into a metric field.
- Deterministic tools (QC, scoring, snapshots, reports) live in code; creative judgment stays with the
  Claude session, which reads and writes the same records.
- External actions (publishing, editing posts) still require the user's approval in the session.

## 5. Staged implementation plan

| Stage | Deliverable | Depends on |
|---|---|---|
| **1 (now)** | Data store + CLI: videos, timestamped metric snapshots, ideas with weighted score, experiments, claims; automated technical QC report for every render; seed with the 25 published videos and today's measurements | Nothing external |
| 2 | Analytics ingestion: Studio metrics (stayed-to-watch, % viewed, traffic sources) at 24 h / 72 h / 7 d; diagnostic scenarios A–F as rules over snapshots | YouTube Studio access (vidIQ authorization or signed-in Studio in the browser pane) |
| 3 | Idea + hook engine records for the next 10 videos (3 hooks each, scored), first controlled experiment (e.g., hook type, duration 25 s vs 40 s) | Stage 1 |
| 4 | Dashboard (HTML artifact) over the data store, separating measured data from interpretations | Stages 1–2 |
| 5 | Next example Short produced end-to-end through the registry, with full scene spec and QC report | ElevenLabs credits or API key |

## 6. External dependencies (exact)

1. **YouTube Studio metrics:** authorize the channel in vidIQ (vidIQ credits reset 2026-12-03), or
   sign in to YouTube Studio in the Claude browser pane so the session can read the Shorts analytics.
2. **Voice:** ElevenLabs connector workspace has ~96 credits left; either top up that workspace or set
   `ELEVENLABS_API_KEY` for a paid account (the user sets it; never pasted in chat).
3. **Research volumes:** vidIQ credits (reset 2026-12-03).

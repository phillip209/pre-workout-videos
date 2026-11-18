# Growth engine — operating procedure (stage 1)

Run from `C:\dev\pre-workout-videos\studio` with the uv Python and `PYTHONPATH=.deps;.`:

```powershell
$env:PYTHONPATH = "$PWD\.deps;$PWD"
$py = "$env:APPDATA\uv\python\cpython-3.12.16-windows-x86_64-none\python.exe"
& $py -m growth report                 # videos + latest measured public views
& $py -m growth qc b04_alcohol         # technical QC of out/b04_alcohol/b04_alcohol.mp4, saved to data/qc_reports.json
& $py -m growth snapshot b04_alcohol youtube_studio stayed_to_watch_pct=61.5 avg_pct_viewed=72
& $py -m growth idea path\to\idea.json  # stores the idea with its weighted score (spec §8)
& $py -m growth ideas                  # ranked; ideas with evidence "insufficient" sink to the bottom
& $py -m unittest growth.test_growth   # tests
```

## Data (studio/data/, versioned in git)

| File | Contents |
|---|---|
| `videos.json` | one row per published Short: slug, YouTube id, title, publication time, format, series, notes |
| `snapshots.json` | timestamped metric snapshots: `source`, `provenance` (`measured`/`calculated`/`ai_interpretation`), metrics. Only numbers read from a real source are stored as `measured`; unknown metric names and non-numbers are rejected |
| `qc_reports.json` | automated checks + pending manual checklist per render; status `blocked` or `needs_manual_review` |
| `ideas.json`, `experiments.json`, `claims.json` | created on first use |

## Per-video workflow (current)

1. Idea record with 8 ratings → weighted score; evidence level recorded (`strong`/`moderate`/`preliminary`/`insufficient`).
2. Script + 3 hooks (Spanish), claims recorded with source, population and limits.
3. Render with `build.py`, then `python -m growth qc <slug>`. A `blocked` report returns to production.
4. Manual checklist in the report (hook, conflict, payoff, consistency, subtitles, claims, metadata).
5. Publish through Metricool only after the user approves.
6. Snapshots at 24 h, 72 h and 7 d. Public views can always be recorded; Studio metrics need access (see assessment §6).

## QC thresholds (studio/growth/qc.py → SPEC)

1080×1920, 30 fps, 15–60 s, clean decode, −14 ± 2 LUFS, true peak ≤ −0.5 dBFS, no black segment > 0.5 s,
no still picture > 0.7 s (channel standard), narration starts ≤ 0.6 s, real (not estimated) voice timing.

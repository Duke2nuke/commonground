# CommonGround — local test log (actual output, 31 Oct 2026, pre-deadline build)

Environment: Python 3.12.3, venv, Flask 3.1.3, requests. No QLOO_API_KEY
set in this environment, so live Qloo was NOT tested and NOT faked.

Command: `.venv/bin/python app.py` (port 5000), then curl checks.

## 1. Health
GET /api/health -> `{"mode":"demo","status":"ok"}`

## 2. Demo plan (POST /api/plan, demo=true, Maya/Leo/Ana, Bengaluru)
- mode: demo, common_ground_score: 0.88
- Film winner: Interstellar — score 0.857 (mean 0.827, min 0.72, coverage 3/3)
  Runners-up: Dune: Part Two (0.825), Everything Everywhere All at Once (0.779)
- Eat winner: The Common Table, Bengaluru — score 0.851 (mean 0.79, min 0.78, coverage 3/3)
  Runners-up: Spice Route Kitchen (0.819), Trattoria Luna (0.817)
- Music winner: Hans Zimmer — score 0.933 (mean 0.913, min 0.88, coverage 3/3)
  Runners-up: A.R. Rahman (0.83), Coldplay (0.785)
- Why it matters: no winner is a single person's runaway favourite;
  every winner has a minimum affinity >= 0.72. That is the fairness term working.

## 3. Homepage
GET / returns the UI and contains the "DEMO MODE" banner text.

## 4. Live call without a key (honesty check)
POST /api/plan without demo=true and without QLOO_API_KEY ->
`{"error":"No QLOO_API_KEY set","hint":"Set QLOO_API_KEY and try again, or use the demo group."}`
HTTP 502. No fake live result was returned.

## Not tested (needs a key / hosting)
- Live Qloo /search + /v2/insights end-to-end.
- Public hosting / demo link.
- Devpost submission (deliberately not submitted by this build).

## 5. Qloo hackathon kit integration (31 Oct 2026, ~01:45 IST)
- Live path rewired to the official kit: `qloo api search` / `qloo api insights`
  from `@qloo/qloo-harness` v0.1.26, verified by `--dry-run` request shapes
  (GET https://api.qloo.com/search, GET https://api.qloo.com/v2/insights
  with filter.type, signal.interests.entities, feature.explainability=true,
  filter.location.query for places). Direct-API client removed.
- Live call without a key still returns an honest error, no fake result.
- Demo mode unchanged and re-tested above: score 0.88.
- Live end-to-end test still pending: needs the event-issued key.

# CommonGround — one evening everyone actually wants

**Problem:** 2–4 people can never agree on a night out. One person picks,
someone else vetoes, and the group defaults to "whatever, you choose."

**CommonGround** is a group taste negotiator. Each person enters 2–3
favourites (a film, an artist, a restaurant/cuisine, anything) plus a city.
The agent uses **Qloo's cross-category taste graph** to find the overlap,
then builds **one complete evening**: a film, a place to eat, and a music
vibe — with a plain-English explanation for each pick showing *which
person's taste it bridges and why*.

## Why it does not work the same without Qloo

A generic LLM list can invent a plausible evening. It cannot tell you,
from a real taste graph, that a pick scores 0.91 with one person and
0.88 with another, or that it appeared in both people's affinity lists.
CommonGround's picks, affinity bars, and "why this pick" text all come
from Qloo affinity data. Remove Qloo and the negotiation has nothing to
negotiate over — that is the point.

## How it works

1. **Resolve** — each favourite name is resolved to a Qloo entity id via
   `GET {base}/search` (`X-Api-Key` header).
2. **Affinity, per person** — for each person and each target category
   (`urn:entity:movie`, `urn:entity:place`, `urn:entity:artist`),
   `GET {base}/v2/insights` is called with
   `signal.interests.entities=<that person's seeds>` and
   `feature.explainability=true`. For places, a location filter is tried
   first and retried without it if Qloo rejects it; both attempts are logged.
3. **Negotiate** — for each category, candidates are scored as
   `0.5 × mean affinity + 0.3 × coverage + 0.2 × minimum affinity`,
   where coverage is the share of people scoring ≥ 0.55. The minimum term
   is the fairness term: a pick one person hates cannot win even if
   another person loves it. See `negotiator.py`.
4. **Explain** — the winner's card names who it bridges, its mean /
   lowest / coverage scores, and the Qloo explainability tags when present.
5. **Share** — a plain-text plan (film + eat + music + scores) can be
   copied in one click.

Every Qloo call made is shown in the UI under "Qloo calls made".

## Run it

```bash
cd qloo-commonground
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# Live mode:
export QLOO_API_KEY="your-qloo-hackathon-key"
# Optional: export QLOO_BASE_URL="https://staging.api.qloo.com"
.venv/bin/python app.py
# Open http://127.0.0.1:5000
```

## DEMO MODE — read this before judging

If `QLOO_API_KEY` is **not** set, the app runs in **clearly labelled
DEMO MODE** on a small curated sample dataset (`demo_data.py`) so the UI
is fully demoable end-to-end. The banner, the plan header, and the calls
log all say DEMO MODE. **Demo results are not live Qloo results and are
never presented as such.** The demo is scored by the exact same
negotiator code as live mode, so switching to live is a key change,
not a code change. A live call without a key returns HTTP 502 with
"No QLOO_API_KEY set" rather than a faked result.

## Project layout

| File | What it is |
|---|---|
| `app.py` | Flask backend, `/`, `/api/plan`, `/api/demo-group`, `/api/health` |
| `qloo_client.py` | Clean Qloo client: search, insights, explainability, call audit log |
| `negotiator.py` | Deterministic fairness scoring + plain-English explanations |
| `demo_data.py` | Labelled demo dataset (demo mode only) |
| `templates/index.html` | Single polished, mobile-friendly UI, no build step |
| `requirements.txt` | Flask, requests |
| `.env.example` | Key / base URL template (never commit a real key) |
| `LICENSE` | MIT |

## Judging-criteria mapping

- **Implementation** — Real Qloo integration (search → per-person insights
  → explainability), a deterministic negotiator, a live call audit log,
  and graceful failure (502, not fake data) when the key is missing.
- **Design** — One page, mobile-friendly, under-30-seconds demo group,
  affinity bars per person, runners-up shown so judges can see the
  negotiation, not just the winner.
- **Impact** — The "what do we do tonight?" argument is universal; the
  fairness score means the plan is one the whole group can actually
  enjoy, which is what makes people reuse it.
- **Idea** — Taste negotiation, not taste recommendation: the product is
  the *overlap*, and Qloo's cross-category graph is the only reason
  a film favourite can legitimately influence a restaurant pick.

## Test log

See `TEST_LOG.md` for the actual local test output (demo plan, health,
homepage DEMO MODE banner, live-without-key 502). No live Qloo test
was faked: no key was available in this environment.

## Limitations (honest)

- Live place results are not guaranteed to be geo-filtered to the typed
  city if Qloo rejects the location filter — the retry path is logged.
- Live candidate names/tags depend on what Qloo returns for the group's
  seeds; unusual favourites may resolve poorly or not at all, in which
  case the API returns an error naming the person whose favourites
  failed to resolve.
- No LLM is used for picks; explanations are templated from scores,
  bridges, and Qloo explainability tags. That is deliberate: the scores
  must stay traceable to Qloo.

## Deploy (public demo, for Devpost)
Render: create a new Web Service from the repo, build `pip install -r requirements.txt`, start `gunicorn app:app --bind 0.0.0.0:$PORT` (see Procfile / render.yaml). Set env var `QLOO_API_KEY` in Render — never commit it. Verify the live demo group at the Render URL before submitting; local-only does not qualify for Qloo.

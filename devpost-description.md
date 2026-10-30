# CommonGround — Devpost description (draft, not yet submitted)

## Inspiration
Every group has lived this: four people, four different tastes, and a
night out that ends in "whatever, you choose." Recommendation apps solve
the one-person problem. Nobody was solving the group problem.

## What it does
CommonGround is a group taste negotiator. 2–4 people enter 2–3 favourites
each — a film, an artist, a cuisine, anything — plus a city. It uses
Qloo's cross-category taste graph to find the overlap, then builds ONE
complete evening: a film, a place to eat, and a music vibe. Each pick
comes with a plain-English explanation naming whose taste it bridges and
why, plus per-person affinity bars and runners-up so you can see the
negotiation, not just the answer. A shareable plan can be copied in one
click, and a pre-filled demo group lets a judge try it in under 30 seconds.

## How we built it
Flask (Python) backend, single HTML/CSS/JS frontend with no build step.
Favourites are resolved to Qloo entity ids via Qloo /search, then
per-person /v2/insights calls (feature.explainability=true) for movies,
places, and artists build the affinity lists. Picks are scored
deterministically: 50% mean affinity, 30% coverage, 20% lowest affinity —
so one person's favourite cannot steamroll the group. Every Qloo call is
shown in the UI's transparency log.

## Challenges we ran into
Designing a score that is fair, not just high-averaging: a pure mean lets
one enthusiastic person win every category. Adding the minimum-affinity
term fixed that, and the demo plan proves it — the winning film, venue,
and artist are compromises with high minimums, not any single person's
top pick. We also made failure honest: without a Qloo API key the app
runs in clearly labelled DEMO MODE on sample data and returns an error,
not a faked live result, for live calls.

## Accomplishments that we're proud of
A working, demoable negotiator end-to-end in one night: live Qloo client
with explainability and a call audit log, a fairness-first scorer, a
polished mobile-friendly UI, and a demo that genuinely shows compromise
(overall common-ground score 0.88 on the demo group).

## What we learned
Taste is a graph problem before it is a language problem: once you have
real per-person affinities, the negotiation is arithmetic, and the
explanation writes itself from the scores. And honesty is a feature —
labelling demo data clearly builds more trust with judges than a
polished-looking fake result ever would.

## What's next for CommonGround
Live Qloo key in, then: real geo-filtered venues for the typed city,
a saved-plan link per group, and a "veto" button so one person can rule
a pick out and watch the negotiation re-run live.

## Built With
Python, Flask, Qloo Taste AI API, HTML, CSS, JavaScript. No paid APIs, no GPU.

## Honest status note for submission
At the time of writing, this project was tested locally in DEMO MODE
because no Qloo API key was available in the build environment. Set
QLOO_API_KEY to run it live; the code path is identical. Do not remove
this note until a live test with a real key has been run and recorded.

"""CommonGround — a group taste negotiator, powered by Qloo.

Flask backend, no GPU, no paid APIs, no LLM in the loop: the picks
come from Qloo affinity lists, and the negotiation is deterministic
arithmetic over those affinities (see negotiator.py).

Modes:
  LIVE — QLOO_API_KEY is set. Favourites are resolved via Qloo /search,
         then per-person /v2/insights calls (feature.explainability=true)
         build the affinity lists the negotiator scores.
  DEMO — no key. A clearly labelled curated dataset is scored by the
         exact same negotiator. The UI banner says DEMO MODE and how
         to switch to live. Demo results are NEVER presented as Qloo's.
"""
from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request

from demo_data import DEMO_CANDIDATES, DEMO_GROUP
from negotiator import CATEGORIES, negotiate, why_text
from qloo_kit_client import QlooKitClient as QlooClient, QlooError

app = Flask(__name__)


def _demo_plan() -> dict:
    people = [p["name"] for p in DEMO_GROUP["people"]]
    plan = negotiate(DEMO_CANDIDATES, people)
    return _finish_plan(plan, people, DEMO_GROUP["city"], mode="demo", calls=[])


def _finish_plan(plan: dict, people: list[str], city: str, mode: str, calls: list) -> dict:
    out = {"mode": mode, "city": city, "people": people,
           "common_ground_score": plan["common_ground_score"], "calls": calls, "plan": {}}
    for key in ("film", "eat", "music"):
        winner = plan[key]["winner"]
        out["plan"][key] = {
            "winner": ({**winner, "why": why_text(winner, people)} if winner else None),
            "runners_up": plan[key]["runners_up"],
        }
    return out


def _live_plan(people_in: list[dict], city: str) -> dict:
    client = QlooClient()
    if not client.live:
        raise QlooError("No QLOO_API_KEY set, or the qloo harness is not installed (npm install --global @qloo/qloo-harness)")
    # 1) Resolve every favourite to a Qloo entity id.
    resolved: dict[str, list[dict]] = {}
    for person in people_in:
        seeds = []
        for fav in person["favourites"]:
            ent = client.search_entity(fav)
            if ent and ent["id"]:
                seeds.append(ent)
        if not seeds:
            raise QlooError(f"Could not resolve any favourite for {person['name']} via Qloo search")
        resolved[person["name"]] = seeds
    # 2) Per-person affinity lists per category, from Qloo insights.
    candidates: dict[str, list[dict]] = {}
    for type_urn, _key, _emoji in CATEGORIES:
        by_name: dict[str, dict] = {}
        for person in people_in:
            seed_ids = [s["id"] for s in resolved[person["name"]]]
            for rec in client.insights(seed_ids, type_urn, location_query=city if type_urn == "urn:entity:place" else None):
                entry = by_name.setdefault(rec["name"], {
                    "name": rec["name"], "tags": rec["tags"],
                    "affinity_by_person": {}, "blurb": ""})
                if rec["affinity"] is not None:
                    entry["affinity_by_person"][person["name"]] = rec["affinity"]
                if rec["explainability"]:
                    entry["blurb"] = "Qloo explainability: " + ", ".join(
                        str(e.get("name") or e) for e in rec["explainability"][:3])
        candidates[type_urn] = list(by_name.values())
    people = [p["name"] for p in people_in]
    plan = negotiate(candidates, people)
    return _finish_plan(plan, people, city, mode="live", calls=client.calls)


@app.route("/")
def index():
    return render_template("index.html", demo_group=DEMO_GROUP,
                           demo_mode=not os.environ.get("QLOO_API_KEY"))


@app.route("/api/plan", methods=["POST"])
def plan():
    data = request.get_json(force=True, silent=True) or {}
    city = (data.get("city") or "").strip() or "Your city"
    raw_people = [p for p in data.get("people", []) if (p.get("name") or "").strip()]
    if not (2 <= len(raw_people) <= 4):
        return jsonify({"error": "Add 2–4 people."}), 400
    people_in = []
    for p in raw_people:
        favs = [f.strip() for f in str(p.get("favourites", "")).split(",") if f.strip()]
        if not (1 <= len(favs) <= 3):
            return jsonify({"error": f"{p['name']}: enter 1–3 favourites, comma-separated."}), 400
        people_in.append({"name": p["name"].strip(), "favourites": favs})
    if data.get("demo"):
        return jsonify(_demo_plan())
    try:
        return jsonify(_live_plan(people_in, city))
    except QlooError as exc:
        return jsonify({"error": str(exc), "hint": "Set QLOO_API_KEY and try again, or use the demo group."}), 502


@app.route("/api/demo-group")
def demo_group():
    return jsonify(DEMO_GROUP)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "mode": "live" if os.environ.get("QLOO_API_KEY") else "demo"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

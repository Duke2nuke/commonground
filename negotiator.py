"""The negotiation: pick ONE film, ONE place, ONE music vibe that the
whole group can live with — not the highest average, and not one
person's favourite steamrolling everyone else.

Score for a candidate, from per-person affinities a in [0, 1]:
    score = 0.5 * mean(a) + 0.3 * coverage + 0.2 * min(a)
    coverage = share of people with affinity >= 0.55

The minimum term is the fairness term: a pick that one person hates
cannot win even if another person loves it. Coverage rewards picks
that bridge multiple people. This is why CommonGround does not work
the same without Qloo — the per-person affinity lists are Qloo's
taste graph, not a generic list, and the explanation names exactly
which people's lists the pick appeared in.
"""
from __future__ import annotations

CATEGORIES = [
    ("urn:entity:movie", "film", "🎬"),
    ("urn:entity:place", "eat", "🍽️"),
    ("urn:entity:artist", "music", "🎵"),
]


def score_candidate(affinities: list[float]) -> dict:
    vals = [max(0.0, min(1.0, float(a))) for a in affinities]
    mean = sum(vals) / len(vals) if vals else 0.0
    minimum = min(vals) if vals else 0.0
    coverage = sum(1 for a in vals if a >= 0.55) / len(vals) if vals else 0.0
    score = 0.5 * mean + 0.3 * coverage + 0.2 * minimum
    return {"score": round(score, 3), "mean": round(mean, 3),
            "min": round(minimum, 3), "coverage": round(coverage, 3)}


def negotiate(candidates_by_type: dict, people: list[str]) -> dict:
    """candidates_by_type: type -> list of {name, tags, affinity_by_person, blurb?}
    Returns one winning pick per category plus runners-up, all scored."""
    plan: dict = {}
    for type_urn, key, _emoji in CATEGORIES:
        scored = []
        for cand in candidates_by_type.get(type_urn, []):
            affs = [cand["affinity_by_person"].get(p, 0.0) for p in people]
            s = score_candidate(affs)
            bridged = [p for p, a in zip(people, affs) if a >= 0.55]
            scored.append({
                "name": cand["name"], "tags": cand.get("tags", []),
                "blurb": cand.get("blurb", ""),
                "affinity_by_person": {p: round(float(a), 2) for p, a in zip(people, affs)},
                "bridged": bridged, **s,
            })
        scored.sort(key=lambda c: c["score"], reverse=True)
        plan[key] = {"winner": scored[0] if scored else None,
                     "runners_up": scored[1:3]}
    overall = [plan[k]["winner"]["score"] for k in ("film", "eat", "music")
               if plan[k]["winner"]]
    plan["common_ground_score"] = round(sum(overall) / len(overall), 3) if overall else 0.0
    return plan


def why_text(pick: dict, people: list[str]) -> str:
    """Plain-English explanation naming who it bridges and why."""
    if not pick:
        return "No candidate was available in this category."
    bridged = pick["bridged"]
    if len(bridged) == len(people):
        who = "everyone in the group"
    elif len(bridged) >= 2:
        who = " and ".join(bridged)
    elif bridged:
        who = f"mainly {bridged[0]}"
    else:
        who = "the group as a compromise"
    weakest = min(pick["affinity_by_person"], key=pick["affinity_by_person"].get)
    return (f"Bridges {who}: group score {pick['score']:.2f} "
            f"(mean {pick['mean']:.2f}, lowest {pick['min']:.2f} for {weakest}, "
            f"coverage {int(pick['coverage'] * len(people))}/{len(people)}). "
            f"{pick['blurb']}")

"""Curated DEMO dataset — clearly labelled, never presented as live Qloo data.

Structure mirrors the live path exactly: per-person affinity lists per
category, so the same negotiator code scores demo and live candidates.
Affinities are illustrative (0-1) and were chosen so the winning plan is
a genuine compromise, not one person's favourite winning outright.
"""
from __future__ import annotations

DEMO_GROUP = {
    "city": "Bengaluru",
    "people": [
        {"name": "Maya", "favourites": ["Dune", "A.R. Rahman", "Sushi"]},
        {"name": "Leo", "favourites": ["Interstellar", "Coldplay", "Italian"]},
        {"name": "Ana", "favourites": ["La La Land", "Hans Zimmer", "Indian"]},
    ],
}

# candidate -> {person: affinity}
DEMO_CANDIDATES = {
    "urn:entity:movie": [
        {"name": "Dune: Part Two", "tags": ["sci-fi", "epic", "visual spectacle"],
         "affinity_by_person": {"Maya": 0.96, "Leo": 0.78, "Ana": 0.64},
         "blurb": "An epic sci-fi spectacle — Maya's world-building, Leo's scale, Ana's score-driven emotion."},
        {"name": "Interstellar", "tags": ["sci-fi", "emotional", "score-driven"],
         "affinity_by_person": {"Maya": 0.72, "Leo": 0.95, "Ana": 0.81},
         "blurb": "Space, stakes and a score you feel in your chest — strong for all three."},
        {"name": "Everything Everywhere All at Once", "tags": ["inventive", "emotional", "genre-bending"],
         "affinity_by_person": {"Maya": 0.68, "Leo": 0.66, "Ana": 0.74},
         "blurb": "Inventive and heartfelt — nobody's first pick, nobody's veto either."},
        {"name": "La La Land", "tags": ["musical", "romantic", "score-driven"],
         "affinity_by_person": {"Maya": 0.52, "Leo": 0.48, "Ana": 0.94},
         "blurb": "Ana's favourite energy, but the weakest bridge across the group."},
    ],
    "urn:entity:place": [
        {"name": "Sushi & Soul, Bengaluru", "tags": ["sushi", "calm", "evening"],
         "affinity_by_person": {"Maya": 0.93, "Leo": 0.62, "Ana": 0.58},
         "blurb": "Maya's sushi pick, with a calm room Leo and Ana can both enjoy."},
        {"name": "Trattoria Luna, Bengaluru", "tags": ["italian", "warm", "shareable"],
         "affinity_by_person": {"Maya": 0.66, "Leo": 0.94, "Ana": 0.71},
         "blurb": "Leo's Italian comfort food, in shareable plates the whole table can split."},
        {"name": "Spice Route Kitchen, Bengaluru", "tags": ["indian", "shareable", "lively"],
         "affinity_by_person": {"Maya": 0.70, "Leo": 0.68, "Ana": 0.92},
         "blurb": "Ana's Indian flavours, served family-style so the group eats together."},
        {"name": "The Common Table, Bengaluru", "tags": ["fusion", "shareable", "lively"],
         "affinity_by_person": {"Maya": 0.78, "Leo": 0.80, "Ana": 0.79},
         "blurb": "A fusion table built for sharing — the highest minimum score of any venue."},
    ],
    "urn:entity:artist": [
        {"name": "Hans Zimmer", "tags": ["cinematic", "score-driven", "epic"],
         "affinity_by_person": {"Maya": 0.88, "Leo": 0.91, "Ana": 0.95},
         "blurb": "The evening's sound: cinematic, epic, and loved by everyone at the table."},
        {"name": "A.R. Rahman", "tags": ["melodic", "cinematic", "cross-cultural"],
         "affinity_by_person": {"Maya": 0.95, "Leo": 0.64, "Ana": 0.82},
         "blurb": "Maya's melodic pick, with a cinematic sweep the others already enjoy."},
        {"name": "Coldplay", "tags": ["anthemic", "uplifting", "singalong"],
         "affinity_by_person": {"Maya": 0.60, "Leo": 0.93, "Ana": 0.66},
         "blurb": "Leo's anthemic energy for the walk home — uplifting, never divisive."},
    ],
}

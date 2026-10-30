"""Live Qloo access via the official Qloo hackathon kit.

The kit (https://github.com/qloo/qloo-hackathon-kit) is the supported
surface for this event: ``qloo api search`` and ``qloo api insights``
from the public ``@qloo/qloo-harness`` npm package (v0.1.26+).
CommonGround does NOT call the Qloo API directly in live mode, and
never silently falls back to another endpoint or credential — if the
kit call fails, the error is surfaced, not papered over.

Verified with ``--dry-run`` (no key needed for the request shape):
  qloo api search  -> GET https://api.qloo.com/search
  qloo api insights -> GET https://api.qloo.com/v2/insights
    with filter.type, signal.interests.entities,
    feature.explainability=true, and filter.location.query for places.

Setup (host side, key never committed):
  npm install --global @qloo/qloo-harness   # Node 22.19+
  export QLOO_API_KEY="<event key>"          # or: qloo setup --qloo
Live mode only when QLOO_API_KEY is set. No key -> the caller must use
demo mode; this client never invents a live result.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess

# Qloo entity URN -> kit alias (from `qloo api insights --help`)
ALIASES = {
    "urn:entity:movie": "movie",
    "urn:entity:place": "place",
    "urn:entity:artist": "artist",
}


class QlooError(Exception):
    """Raised when the kit / Qloo returns an error or unusable output."""


class QlooKitClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("QLOO_API_KEY", "").strip()
        self.calls: list[dict] = []  # audit log, shown in the UI

    @property
    def live(self) -> bool:
        return bool(self.api_key) and shutil.which("qloo") is not None

    def _run(self, argv: list[str]) -> dict:
        cmd = ["qloo", "api"] + argv + ["--json"]
        self.calls.append({"method": "qloo api", "url": " ".join(cmd), "params": {}})
        env = dict(os.environ, QLOO_API_KEY=self.api_key)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise QlooError(f"qloo harness failed: {exc}") from exc
        out = (proc.stdout or "").strip()
        if not out:
            raise QlooError(f"qloo harness returned no output: {proc.stderr[:300]}")
        try:
            data = json.loads(out)
        except ValueError as exc:
            raise QlooError(f"qloo harness returned non-JSON: {out[:300]}") from exc
        if isinstance(data, dict) and data.get("error"):
            raise QlooError(f"Qloo via kit: {data.get('message') or data.get('code')}")
        return data

    def search_entity(self, query: str) -> dict | None:
        """Resolve a free-text favourite to its first Qloo entity, or None."""
        data = self._run(["search", "-q", query, "-n", "3"])
        results = data.get("results") or data.get("entities") or []
        if not results:
            return None
        first = results[0]
        entity = first.get("entity") or first
        return {
            "id": entity.get("entity_id") or entity.get("id"),
            "name": entity.get("name") or query,
            "type": entity.get("type"),
        }

    def insights(self, seed_ids: list[str], target_type: str, location_query: str | None = None) -> list[dict]:
        """Affinity recommendations for one target category.

        target_type is a Qloo entity URN. For places, a location filter
        is attempted first; if Qloo rejects it, the call is retried
        without it and both attempts stay logged.
        """
        alias = ALIASES.get(target_type, target_type)
        argv = ["insights", "-t", alias, "-s", ",".join(seed_ids), "-n", "20",
                "--params", '{"feature":{"explainability":true}}']
        if target_type == "urn:entity:place" and location_query:
            try:
                return self._normalise(self._run(argv + ["--filter-location", location_query]))
            except QlooError:
                pass  # retry unfiltered, logged
        return self._normalise(self._run(argv))

    @staticmethod
    def _normalise(data: dict) -> list[dict]:
        results = data.get("results") or data.get("entities") or []
        out = []
        for item in results:
            entity = item.get("entity") or item
            affinity = item.get("affinity")
            if affinity is None:
                affinity = item.get("query", {}).get("affinity")
            explain = item.get("explainability") or item.get("explanation") or []
            if isinstance(explain, dict):
                explain = [explain]
            out.append({
                "id": entity.get("entity_id") or entity.get("id"),
                "name": entity.get("name") or "Unknown",
                "type": entity.get("type"),
                "affinity": float(affinity) if affinity is not None else None,
                "tags": [t.get("name") if isinstance(t, dict) else str(t)
                         for t in (entity.get("tags") or [])][:6],
                "explainability": explain,
            })
        return out

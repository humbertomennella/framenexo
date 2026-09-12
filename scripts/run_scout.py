"""Frequent, publication-free source watcher for the Apurante newsroom."""
from __future__ import annotations

import fcntl
import json
import os

import pipeline as p


def summarize(result: dict) -> dict:
    candidates = p.read("data/candidates.json", [])
    by_status: dict[str, int] = {}
    for candidate in candidates:
        status = candidate.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    return {
        "lastRunAt": p.iso(),
        "status": "degraded" if result.get("errors") else "healthy",
        "runId": os.environ.get("GITHUB_RUN_ID"),
        "sourcesReached": result.get("sourcesOK", 0),
        "newCandidates": result.get("collected", 0),
        "sourceErrors": result.get("errors", []),
        "queueByStatus": by_status,
        "publishingAllowed": False,
        "note": "A escuta apenas organiza pautas. Publicação continua sujeita à confirmação independente, mídia autorizada e validação editorial.",
    }


def main() -> None:
    (p.ROOT / ".cache").mkdir(exist_ok=True)
    with (p.ROOT / ".cache/scout.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        started = p.iso()
        try:
            result = p.collect()
            if not result.get("sourcesOK"):
                raise RuntimeError("all_sources_failed")
            state = summarize(result)
            state["startedAt"] = started
            p.write("data/scout-state.json", state)
            p.log("scout_completed", **state)
            print(json.dumps(state, ensure_ascii=False))
        except Exception as error:
            p.write(
                "data/scout-state.json",
                {
                    "startedAt": started,
                    "lastRunAt": p.iso(),
                    "status": "failed",
                    "runId": os.environ.get("GITHUB_RUN_ID"),
                    "error": type(error).__name__,
                    "publishingAllowed": False,
                },
            )
            p.log("error", stage="scout", code=type(error).__name__)
            raise


if __name__ == "__main__":
    main()

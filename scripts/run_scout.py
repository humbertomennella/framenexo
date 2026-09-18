"""Frequent, publication-free source watcher for the Apurante newsroom."""
from __future__ import annotations

import datetime as dt
import fcntl
import json
import os

import pipeline as p
import scout_snapshot as snapshots


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
        "evidenceBackfilled": result.get("evidenceBackfilled", 0),
        "sourceErrors": result.get("errors", []),
        "queueByStatus": by_status,
        "publishingAllowed": False,
        "note": "A escuta apenas organiza pautas. Publicação continua sujeita à confirmação independente, mídia autorizada e validação editorial.",
    }


def backfill_feed_evidence(result: dict) -> int:
    """Refresh missing recent RSS evidence for candidates that were already known."""
    failed = {row.get("source") for row in result.get("errors", [])}
    missing: dict[str, dict[str, dict]] = {}
    current = p.now()

    for item in p.read("data/candidates.json", []):
        if item.get("status") != "candidate":
            continue
        stamp = p.date(item.get("publishedAt"))
        if not stamp or not dt.timedelta(minutes=-5) <= current - stamp <= dt.timedelta(hours=48):
            continue
        ident = item.get("id")
        source_id = item.get("sourceId")
        url = item.get("url")
        if not ident or not source_id or not url:
            continue

        archived = p.read(f'.cache/evidence/{ident}.json', {})
        text = archived.get("text")
        fetched = p.date(archived.get("fetchedAt")) if isinstance(archived.get("fetchedAt"), str) else None
        try:
            same = p.canonical_url(archived.get("url", "")) == p.canonical_url(url)
        except Exception:
            same = False
        fresh = fetched is not None and dt.timedelta(minutes=-5) <= current - fetched <= dt.timedelta(hours=20)
        if same and isinstance(text, str) and len(text.split()) >= 25 and not p.suspicious(text) and fresh:
            continue

        try:
            canonical = p.canonical_url(url)
        except Exception:
            continue
        missing.setdefault(source_id, {})[canonical] = item

    sources = [
        source
        for source in p.read("data/sources.json", [])
        if source.get("enabled")
        and source.get("feed")
        and source.get("id") in missing
        and source.get("id") not in failed
    ]

    restored = 0
    for source in sources:
        try:
            rows = p.parse_feed(p.fetch(source["feed"], source["hosts"]))
        except Exception as error:
            p.log("evidence_backfill_failed", source=source["id"], code=type(error).__name__)
            continue

        targets = missing[source["id"]]
        for row in rows:
            try:
                url = p.canonical_url(row.get("url", ""))
            except Exception:
                continue
            item = targets.get(url)
            if not item:
                continue
            text = row.get("text", "")
            if (
                not isinstance(text, str)
                or len(text.split()) < 25
                or p.suspicious(item.get("title", "") + " " + text)
            ):
                continue
            p.write(
                f'.cache/evidence/{item["id"]}.json',
                {"url": url, "text": text[:18000], "fetchedAt": p.iso()},
            )
            restored += 1

    if restored:
        p.log("evidence_backfilled", restored=restored)
    return restored


def main() -> None:
    (p.ROOT / ".cache").mkdir(exist_ok=True)
    with (p.ROOT / ".cache/scout.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        restore = p.read(".cache/scout/restore.json", {})
        document = p.read(".cache/scout/input.json", {})
        if document:
            payload = snapshots.validate(document)
            seed = payload["candidates"]
            snapshots.restore_evidence(payload)
        elif restore.get("status") == "unavailable":
            # Se o transporte do artifact falhar, ainda podemos fazer uma coleta
            # nova usando apenas o último pool versionado como semente. Nenhuma
            # pauta é publicada por esse fallback: ela continua sujeita a todas
            # as verificações, corroboração independente e validação editorial.
            seed = p.read("data/candidates.json", [])
        else:
            raise RuntimeError("snapshot_restore_required")
        with p.state_paths(snapshots.TRANSIENT):
            p.write("data/candidates.json", snapshots.prune(seed))
            collect_snapshot()


def collect_snapshot():
    started = p.iso()
    (p.ROOT / ".cache/scout/snapshot.json").unlink(missing_ok=True)
    try:
        result = p.collect()
        if not result.get("sourcesOK"):
            raise RuntimeError("all_sources_failed")
        result["evidenceBackfilled"] = backfill_feed_evidence(result)
        p.write("data/candidates.json", snapshots.prune(p.read("data/candidates.json", [])))
        state = summarize(result)
        state["startedAt"] = started
        p.write("data/scout-state.json", state)
        p.log("scout_completed", **state)
        document = snapshots.create(p.read("data/candidates.json", []), state)
        snapshots.validate(document)
        p.write(".cache/scout/snapshot.json", document)
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

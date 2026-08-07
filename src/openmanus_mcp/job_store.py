"""Bounded persistent job store for async OpenManus runs (MCP + API processes).

Completed jobs are evicted FIFO when over ``max_completed`` to cap memory.
Uses a local JSON file for persistence across restarts.
"""

from __future__ import annotations

import json
import logging
from collections import deque
from pathlib import Path
from typing import Any

from openmanus_mcp.runner import RunResult
from openmanus_mcp.settings import get_settings

log = logging.getLogger(__name__)


class JobStore:
    """Stores pending markers and ``RunResult`` values; prunes oldest completed."""

    def __init__(self, file_path: Path | str, max_completed: int = 100) -> None:
        self._path = Path(file_path)

        self._max = max(1, int(max_completed))
        self._jobs: dict[str, RunResult | str] = {}
        self._completed_fifo: deque[str] = deque()
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
                self._jobs = {}
                self._completed_fifo = deque()
                for jid, val in data.items():
                    if isinstance(val, dict):
                        self._jobs[jid] = RunResult.from_dict(val)
                        self._completed_fifo.append(jid)
                    else:
                        self._jobs[jid] = val

            self._evict_completed()
            log.info("job_store_loaded: %s (count=%d)", str(self._path), len(self._jobs))
        except Exception as exc:
            log.error("job_store_load_failed: %s (%s)", str(self._path), str(exc))

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self._path.with_suffix(".tmp")
            data: dict[str, Any] = {}
            for jid, val in self._jobs.items():
                if isinstance(val, RunResult):
                    data[jid] = val.to_dict()
                else:
                    data[jid] = val
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self._path)
        except Exception as exc:
            log.error("job_store_save_failed: %s (%s)", str(self._path), str(exc))

    def set_pending(self, job_id: str) -> None:
        self._jobs[job_id] = "pending"
        self._save()

    def set_result(self, job_id: str, result: RunResult) -> None:
        self._jobs[job_id] = result

        if job_id not in self._completed_fifo:
            self._completed_fifo.append(job_id)

        self._evict_completed()
        self._save()

    def _evict_completed(self) -> None:
        while len(self._completed_fifo) > self._max:
            victim = self._completed_fifo.popleft()
            if victim in self._jobs:
                del self._jobs[victim]

    def get(self, job_id: str) -> RunResult | str | None:
        # Check if it's in memory; if not, reload (simple polling sync between processes)
        if job_id not in self._jobs:
            self._load()
        return self._jobs.get(job_id)

    def pending_count(self) -> int:
        return sum(1 for v in self._jobs.values() if v == "pending")

    def stored_count(self) -> int:
        return len(self._jobs)


_registry: dict[str, JobStore] = {}


def mcp_job_store() -> JobStore:
    """Singleton for the stdio MCP server process."""
    if "mcp" not in _registry:
        s = get_settings()
        # Use a distinct file suffix if shared root but we want isolation;
        # or share the same file for "one fleet" behavior.
        # We share for fleet behavior.
        _registry["mcp"] = JobStore(s.job_store_path, s.job_store_max_completed)
    return _registry["mcp"]


def api_job_store() -> JobStore:
    """Singleton for the FastAPI process."""
    if "api" not in _registry:
        s = get_settings()
        _registry["api"] = JobStore(s.job_store_path, s.job_store_max_completed)
    return _registry["api"]


def reset_job_stores_for_tests() -> None:
    """Clear singletons (pytest only)."""
    _registry.clear()

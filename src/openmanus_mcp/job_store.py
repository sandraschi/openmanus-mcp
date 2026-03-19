"""Bounded in-memory job store for async OpenManus runs (MCP + API processes).

Completed jobs are evicted FIFO when over ``max_completed`` to cap memory.
Pending jobs are never evicted by this logic.
"""

from __future__ import annotations

from collections import deque

from openmanus_mcp.runner import RunResult


class JobStore:
    """Stores pending markers and ``RunResult`` values; prunes oldest completed."""

    def __init__(self, max_completed: int = 100) -> None:
        self._max = max(1, int(max_completed))
        self._jobs: dict[str, RunResult | str] = {}
        self._completed_fifo: deque[str] = deque()

    def set_pending(self, job_id: str) -> None:
        self._jobs[job_id] = "pending"

    def set_result(self, job_id: str, result: RunResult) -> None:
        if job_id not in self._jobs:
            return
        self._jobs[job_id] = result
        self._completed_fifo.append(job_id)
        self._evict_completed()

    def _evict_completed(self) -> None:
        while len(self._completed_fifo) > self._max:
            victim = self._completed_fifo.popleft()
            val = self._jobs.get(victim)
            if isinstance(val, RunResult):
                del self._jobs[victim]

    def get(self, job_id: str) -> RunResult | str | None:
        return self._jobs.get(job_id)

    def pending_count(self) -> int:
        return sum(1 for v in self._jobs.values() if v == "pending")

    def stored_count(self) -> int:
        return len(self._jobs)


_mcp_store: JobStore | None = None
_api_store: JobStore | None = None


def mcp_job_store() -> JobStore:
    """Singleton for the stdio MCP server process."""
    global _mcp_store
    if _mcp_store is None:
        from openmanus_mcp.settings import get_settings

        _mcp_store = JobStore(get_settings().job_store_max_completed)
    return _mcp_store


def api_job_store() -> JobStore:
    """Singleton for the FastAPI process."""
    global _api_store
    if _api_store is None:
        from openmanus_mcp.settings import get_settings

        _api_store = JobStore(get_settings().job_store_max_completed)
    return _api_store


def reset_job_stores_for_tests() -> None:
    """Clear singletons (pytest only)."""
    global _mcp_store, _api_store
    _mcp_store = None
    _api_store = None

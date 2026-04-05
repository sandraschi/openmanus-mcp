"""JobStore FIFO eviction."""

from __future__ import annotations

from openmanus_mcp.job_store import JobStore
from openmanus_mcp.runner import RunResult


def _ok_result(prompt: str = "x") -> RunResult:
    return RunResult(
        success=True,
        entry_point="main.py",
        prompt=prompt,
        stdout="",
        stderr="",
        exit_code=0,
        timed_out=False,
        execution_time_ms=1.0,
    )


def test_evict_oldest_completed(tmp_path: object) -> None:
    f = tmp_path / "jobs.json"
    store = JobStore(file_path=str(f), max_completed=3)
    for i in range(5):
        jid = f"j{i}"
        store.set_pending(jid)
        store.set_result(jid, _ok_result(str(i)))
    # max_completed=3: FIFO drops j0,j1; j2,j3,j4 remain
    assert store.stored_count() == 3
    assert store.get("j0") is None
    assert store.get("j1") is None
    assert store.get("j2") is not None
    assert store.get("j3") is not None
    assert store.get("j4") is not None


def test_pending_not_evicted_by_fifo(tmp_path: object) -> None:
    f = tmp_path / "jobs_fifo.json"
    store = JobStore(file_path=str(f), max_completed=1)
    store.set_pending("a")
    store.set_pending("b")
    store.set_result("a", _ok_result())
    store.set_result("b", _ok_result())
    # Two completed — max 1 — one evicted
    assert store.stored_count() == 1


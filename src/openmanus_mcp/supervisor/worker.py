"""Background supervisor tick: heartbeat + interval schedules → async OpenManus jobs."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any

from openmanus_mcp.concurrency import api_run_limiter
from openmanus_mcp.job_store import api_job_store
from openmanus_mcp.openmanus_detect import describe_openmanus
from openmanus_mcp.runner import EntryPoint, RunResult, run_prompt
from openmanus_mcp.settings import get_settings
from openmanus_mcp.supervisor.schedules import ScheduleEntry, pop_due_schedules
from openmanus_mcp.supervisor.state import (
    bump_schedules_fired,
    heartbeat_update,
    record_tick,
)

log = logging.getLogger(__name__)
_BACKGROUND_TASKS: set[asyncio.Task[Any]] = set()


class SupervisorState:
    """Thread-safe container for supervisor lifecycle events."""

    def __init__(self) -> None:
        self.stop: asyncio.Event | None = None
        self.task: asyncio.Task[None] | None = None


_state = SupervisorState()


async def _fire_scheduled_run(ent: ScheduleEntry) -> None:
    settings = get_settings()
    info = describe_openmanus(settings.openmanus_root)
    if info is None or not info.looks_valid:
        await heartbeat_update(
            last_error="scheduled run skipped: OPENMANUS_ROOT missing or invalid",
        )
        log.warning("supervisor: skip schedule %s — invalid OPENMANUS_ROOT", ent.name)
        return

    ep: EntryPoint = "run_flow.py" if ent.entry_point == "run_flow.py" else "main.py"
    prompt = ent.effective_prompt()
    t_out = settings.runner_timeout_s

    jid = str(uuid.uuid4())
    store = api_job_store()
    store.set_pending(jid)
    await bump_schedules_fired()

    async def _bg() -> None:
        lim = api_run_limiter()
        await lim.acquire()
        try:
            r = await run_prompt(info.root, prompt, ep, t_out)
            store.set_result(jid, r)
            if not r.success:
                await heartbeat_update(last_error=r.error or "scheduled run failed")
        except Exception as exc:
            await heartbeat_update(last_error=str(exc))
            t0 = time.perf_counter()
            store.set_result(
                jid,
                RunResult(
                    success=False,
                    entry_point=ep,
                    prompt=prompt,
                    stdout="",
                    stderr="",
                    exit_code=None,
                    timed_out=False,
                    execution_time_ms=(time.perf_counter() - t0) * 1000,
                    error=str(exc),
                ),
            )
        finally:
            await lim.release()

    task = asyncio.create_task(_bg())
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_BACKGROUND_TASKS.discard)
    log.info("supervisor: queued schedule %s job_id=%s", ent.name, jid)


async def _tick_loop(stop: asyncio.Event) -> None:
    settings = get_settings()
    tick_s = settings.supervisor_tick_s
    await heartbeat_update(
        running=True,
        started_at_monotonic=time.monotonic(),
        last_error=None,
    )
    while not stop.is_set():
        try:
            now = time.monotonic()
            await record_tick()
            due = await pop_due_schedules(now)
            for ent in due:
                await _fire_scheduled_run(ent)
        except Exception as exc:
            await heartbeat_update(last_error=str(exc))
            log.exception("supervisor tick failed")
        try:
            await asyncio.wait_for(stop.wait(), timeout=tick_s)
            break
        except TimeoutError:
            continue
    await heartbeat_update(running=False)


def start_supervisor() -> None:
    """Start background loop if enabled in settings (idempotent)."""
    settings = get_settings()
    if not settings.supervisor_enabled:
        log.info("supervisor disabled (OPENMANUS_SUPERVISOR_ENABLED=false)")
        return
    if _state.task is not None and not _state.task.done():
        return
    _state.stop = asyncio.Event()
    _state.task = asyncio.create_task(_tick_loop(_state.stop), name="openmanus_supervisor")
    log.info("supervisor started tick_s=%s", settings.supervisor_tick_s)


async def stop_supervisor() -> None:
    """Signal worker to stop and await task (best-effort)."""
    if _state.stop is not None:
        _state.stop.set()
    if _state.task is not None:
        try:
            await asyncio.wait_for(_state.task, timeout=5.0)
        except TimeoutError:
            _state.task.cancel()
        _state.task = None
    _state.stop = None

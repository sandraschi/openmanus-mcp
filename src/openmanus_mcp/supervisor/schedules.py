"""In-memory schedule registry (interval-based; persists for process lifetime only)."""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field

EntryPoint = Literal["main.py", "run_flow.py"]


class ScheduleCreate(BaseModel):
    """POST body for new schedule."""

    name: str = Field(min_length=1, max_length=200)
    interval_s: float = Field(gt=0, le=86400 * 7, description="Seconds between runs")
    prompt: str = Field(min_length=1, max_length=50_000)
    entry_point: EntryPoint = "main.py"
    enabled: bool = True
    connector_kind: str | None = Field(
        default=None,
        description="Optional hint: email | yahboom | calibre — prepended to prompt in worker.",
    )


class ScheduleOut(BaseModel):
    id: str
    name: str
    interval_s: float
    prompt: str
    entry_point: EntryPoint
    enabled: bool
    connector_kind: str | None
    last_run_at_monotonic: float | None
    next_due_after_s: float | None
    created_at_monotonic: float


@dataclass
class ScheduleEntry:
    id: str
    name: str
    interval_s: float
    prompt: str
    entry_point: EntryPoint
    enabled: bool
    connector_kind: str | None
    last_run_at_monotonic: float | None = None
    created_at_monotonic: float = field(default_factory=time.monotonic)

    def effective_prompt(self) -> str:
        if not self.connector_kind:
            return self.prompt
        return (
            f"[connector={self.connector_kind}]\n"
            f"Use fleet MCP tools for this connector when available.\n\n"
            f"{self.prompt}"
        )

    def seconds_until_due(self, now: float) -> float:
        if not self.enabled:
            return float("inf")
        if self.last_run_at_monotonic is None:
            return 0.0
        elapsed = now - self.last_run_at_monotonic
        return max(0.0, self.interval_s - elapsed)

    def is_due(self, now: float) -> bool:
        return self.seconds_until_due(now) <= 0.0

    def to_out(self, now: float) -> ScheduleOut:
        due = self.seconds_until_due(now)
        next_due = None if due == float("inf") else due
        return ScheduleOut(
            id=self.id,
            name=self.name,
            interval_s=self.interval_s,
            prompt=self.prompt,
            entry_point=self.entry_point,
            enabled=self.enabled,
            connector_kind=self.connector_kind,
            last_run_at_monotonic=self.last_run_at_monotonic,
            next_due_after_s=next_due,
            created_at_monotonic=self.created_at_monotonic,
        )


_lock = asyncio.Lock()
_schedules: dict[str, ScheduleEntry] = {}


async def list_schedules() -> list[ScheduleOut]:
    now = time.monotonic()
    async with _lock:
        return [s.to_out(now) for s in _schedules.values()]


async def create_schedule(body: ScheduleCreate) -> ScheduleOut:
    sid = str(uuid.uuid4())
    now = time.monotonic()
    async with _lock:
        ent = ScheduleEntry(
            id=sid,
            name=body.name.strip(),
            interval_s=body.interval_s,
            prompt=body.prompt,
            entry_point=body.entry_point,
            enabled=body.enabled,
            connector_kind=(body.connector_kind.strip().lower() if body.connector_kind else None),
            created_at_monotonic=now,
        )
        _schedules[sid] = ent
        return ent.to_out(time.monotonic())


async def delete_schedule(sid: str) -> bool:
    async with _lock:
        if sid not in _schedules:
            return False
        del _schedules[sid]
        return True


async def patch_schedule_enabled(sid: str, enabled: bool) -> ScheduleOut | None:
    now = time.monotonic()
    async with _lock:
        ent = _schedules.get(sid)
        if ent is None:
            return None
        ent.enabled = enabled
        return ent.to_out(now)


async def pop_due_schedules(now: float) -> list[ScheduleEntry]:
    """Return schedules that are due; set last_run_at before return to avoid double-fire."""
    async with _lock:
        due: list[ScheduleEntry] = []
        for ent in list(_schedules.values()):
            if ent.is_due(now):
                ent.last_run_at_monotonic = now
                due.append(ent)
        return due


def schedule_count() -> int:
    return len(_schedules)

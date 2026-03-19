"""Supervisor heartbeat and process-local state (single worker)."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class HeartbeatState:
    """Updated by the supervisor tick loop."""

    running: bool = False
    started_at_monotonic: float | None = None
    tick_count: int = 0
    last_tick_at_monotonic: float | None = None
    last_error: str | None = None
    schedules_fired_total: int = 0

    def to_public_dict(self) -> dict[str, Any]:
        now = time.monotonic()
        uptime_s: float | None = None
        if self.started_at_monotonic is not None:
            uptime_s = round(now - self.started_at_monotonic, 3)
        last_tick_age_s: float | None = None
        if self.last_tick_at_monotonic is not None:
            last_tick_age_s = round(now - self.last_tick_at_monotonic, 3)
        return {
            "running": self.running,
            "uptime_s": uptime_s,
            "tick_count": self.tick_count,
            "last_tick_age_s": last_tick_age_s,
            "last_error": self.last_error,
            "schedules_fired_total": self.schedules_fired_total,
        }


_heartbeat = HeartbeatState()
_lock = asyncio.Lock()


def get_heartbeat() -> HeartbeatState:
    return _heartbeat


async def heartbeat_update(**kwargs: Any) -> None:
    async with _lock:
        for k, v in kwargs.items():
            if hasattr(_heartbeat, k):
                setattr(_heartbeat, k, v)


async def bump_schedules_fired() -> None:
    async with _lock:
        _heartbeat.schedules_fired_total += 1


async def record_tick() -> None:
    async with _lock:
        _heartbeat.tick_count += 1
        _heartbeat.last_tick_at_monotonic = time.monotonic()

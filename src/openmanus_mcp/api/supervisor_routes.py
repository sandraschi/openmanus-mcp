"""Supervisor + connectors REST (OpenClaw-style spine; schedules are in-memory per process)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from openmanus_mcp.connectors import get_connector, list_connectors
from openmanus_mcp.settings import get_settings
from openmanus_mcp.supervisor.schedules import (
    ScheduleCreate,
    ScheduleOut,
    create_schedule,
    delete_schedule,
    list_schedules,
    patch_schedule_enabled,
)
from openmanus_mcp.supervisor.state import get_heartbeat

router = APIRouter(tags=["supervisor"])


class ScheduleEnabledBody(BaseModel):
    enabled: bool


@router.get("/supervisor/heartbeat")
async def supervisor_heartbeat() -> dict[str, Any]:
    """Liveness + tick metrics for the background supervisor (if enabled)."""
    settings = get_settings()
    hb = get_heartbeat().to_public_dict()
    return {
        "supervisor_enabled": settings.supervisor_enabled,
        "supervisor_tick_s": settings.supervisor_tick_s,
        **hb,
    }


@router.get("/supervisor/schedules", response_model=list[ScheduleOut])
async def get_schedules() -> list[ScheduleOut]:
    return await list_schedules()


@router.post("/supervisor/schedules", response_model=ScheduleOut)
async def post_schedule(body: ScheduleCreate) -> ScheduleOut:
    return await create_schedule(body)


@router.delete("/supervisor/schedules/{schedule_id}")
async def remove_schedule(schedule_id: str) -> dict[str, bool]:
    ok = await delete_schedule(schedule_id)
    if not ok:
        raise HTTPException(status_code=404, detail="schedule not found")
    return {"success": True}


@router.patch("/supervisor/schedules/{schedule_id}/enabled", response_model=ScheduleOut)
async def set_schedule_enabled(schedule_id: str, body: ScheduleEnabledBody) -> ScheduleOut:
    out = await patch_schedule_enabled(schedule_id, body.enabled)
    if out is None:
        raise HTTPException(status_code=404, detail="schedule not found")
    return out


@router.get("/connectors")
async def connectors_list() -> dict[str, Any]:
    """Built-in connector catalog (email / yahboom / calibre) — MCP wiring is client-side."""
    return {"connectors": list_connectors()}


@router.get("/connectors/{kind}")
async def connectors_one(kind: str) -> dict[str, Any]:
    data = get_connector(kind)
    if data is None:
        raise HTTPException(status_code=404, detail="unknown connector kind")
    return {"connector": data}

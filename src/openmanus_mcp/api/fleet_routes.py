"""REST endpoints for fleet catalog, onboard, and webapp launch."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter

from openmanus_mcp.fleet.models import (
    OnboardRequest,
    OnboardResponse,
    WebappStartRequest,
    WebappStartResponse,
)
from openmanus_mcp.fleet.service import (
    members_detail,
    merge_catalog_rows,
    onboard_many,
    resolve_fleet_root,
    start_webapp,
)
from openmanus_mcp.settings import get_settings

router = APIRouter(prefix="/fleet", tags=["fleet"])


def _fleet_root() -> Path:
    s = get_settings()
    return resolve_fleet_root(s.openmanus_fleet_root)


@router.get("/catalog")
async def fleet_catalog() -> dict[str, Any]:
    rows = merge_catalog_rows(_fleet_root())
    return {
        "success": True,
        "members": [r.model_dump() for r in rows],
    }


@router.get("/members")
async def fleet_members() -> dict[str, Any]:
    return {"success": True, "members": members_detail(_fleet_root())}


@router.post("/onboard")
async def fleet_onboard(body: OnboardRequest) -> OnboardResponse:
    return onboard_many(_fleet_root(), body)


@router.post("/webapp/start")
async def fleet_webapp_start(body: WebappStartRequest) -> WebappStartResponse:
    return start_webapp(_fleet_root(), body)

"""Pydantic models for fleet catalog and API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class InstallSpec(BaseModel):
    kind: Literal["none", "uv_pip_editable", "uv_sync_extra_dev"]


class WebappSpec(BaseModel):
    kind: Literal["powershell_script"] = "powershell_script"
    script_relative: str = Field(
        ...,
        description="Path relative to clone root, e.g. web_sota/start.ps1",
    )


class CatalogMember(BaseModel):
    id: str
    name: str
    category: str
    description: str
    github_repo: str
    install: InstallSpec
    webapp: WebappSpec | None = None


class FleetCatalogFile(BaseModel):
    version: int
    members: list[CatalogMember]


class OnboardedMember(BaseModel):
    clone_path: str
    onboarded_at: str
    install_ok: bool
    install_log: str
    last_webapp_pid: int | None = None


class FleetStateFile(BaseModel):
    members: dict[str, OnboardedMember] = Field(default_factory=dict)


class CatalogRow(CatalogMember):
    """Catalog entry plus live status for the UI."""

    onboarded: bool = False
    clone_path: str | None = None
    install_ok: bool | None = None


class OnboardRequest(BaseModel):
    member_ids: list[str]


class OnboardResult(BaseModel):
    member_id: str
    success: bool
    message: str
    clone_path: str | None = None


class OnboardResponse(BaseModel):
    success: bool
    results: list[OnboardResult]


class WebappStartRequest(BaseModel):
    member_id: str


class WebappStartResponse(BaseModel):
    success: bool
    message: str
    pid: int | None = None
    command: list[str] | None = None


class FleetMembersResponse(BaseModel):
    success: bool
    members: dict[str, Any]

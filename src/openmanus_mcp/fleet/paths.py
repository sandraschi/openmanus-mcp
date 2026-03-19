"""Resolve repository root and fleet directory (on-disk workspace for clones)."""

from __future__ import annotations

from pathlib import Path


def default_repo_root() -> Path:
    """Git root of openmanus-mcp when running from source (four parents above fleet/paths.py)."""
    return Path(__file__).resolve().parent.parent.parent.parent


def default_fleet_root() -> Path:
    """``fleet/`` next to repo root in dev; override with OPENMANUS_FLEET_ROOT."""
    return default_repo_root() / "fleet"

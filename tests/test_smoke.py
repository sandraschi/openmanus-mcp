"""Smoke tests — no OpenManus clone required."""

import pytest

from openmanus_mcp.openmanus_detect import describe_openmanus
from openmanus_mcp.server import openmanus_bridge


def test_describe_none() -> None:
    assert describe_openmanus(None) is None


@pytest.mark.asyncio
async def test_bridge_status() -> None:
    r = await openmanus_bridge("status")
    assert r["success"] is True
    assert r["result"]["server_version"] == "0.1.0"

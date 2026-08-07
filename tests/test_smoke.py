"""Smoke tests — no OpenManus clone required."""

import pytest

from openmanus_mcp import __version__
from openmanus_mcp.openmanus_detect import describe_openmanus
from openmanus_mcp.server import openmanus_bridge


def test_describe_none() -> None:
    assert describe_openmanus(None) is None


@pytest.mark.asyncio
async def test_bridge_status() -> None:
    r = await openmanus_bridge("status")
    assert r["success"] is True
    assert r["result"]["server_version"] == __version__
    assert "runner_timeout_s" in r["result"]
    assert "async_jobs_pending" in r["result"]
    assert "async_jobs_stored" in r["result"]
    assert "job_store_path" in r["result"]


@pytest.mark.asyncio
async def test_bridge_unknown_op() -> None:
    r = await openmanus_bridge("bogus_operation")
    assert r["success"] is False
    assert r["error_type"] == "invalid_argument"

"""Reset job-store singletons between tests."""

from __future__ import annotations

import pytest

from openmanus_mcp.job_store import reset_job_stores_for_tests


@pytest.fixture(autouse=True)
def _reset_job_stores() -> object:
    reset_job_stores_for_tests()
    yield
    reset_job_stores_for_tests()

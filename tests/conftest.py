"""Reset job-store singletons between tests; isolate OPENMANUS_ROOT for API tests."""

from __future__ import annotations

import pytest

from openmanus_mcp.job_store import reset_job_stores_for_tests


@pytest.fixture(scope="session")
def _pytest_openmanus_root_dir(tmp_path_factory: pytest.TempPathFactory) -> str:
    """Empty directory (no main.py) so describe_openmanus is invalid unless overridden."""
    p = tmp_path_factory.mktemp("openmanus_root_empty")
    return str(p)


@pytest.fixture(autouse=True)
def _force_test_openmanus_root(
    monkeypatch: pytest.MonkeyPatch, _pytest_openmanus_root_dir: str
) -> None:
    """Prevent developer .env OPENMANUS_ROOT from spawning real OpenManus during TestClient runs."""
    monkeypatch.setenv("OPENMANUS_ROOT", _pytest_openmanus_root_dir)


    yield
    reset_job_stores_for_tests()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom cli options for FastMCP 3.2 SOTA testing."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run real integration tests (requires OPENMANUS_ROOT)",
    )


@pytest.fixture
def is_integration(request: pytest.FixtureRequest) -> bool:
    """Boolean flag to skip or branch based on --integration cli arg."""
    return bool(request.config.getoption("--integration"))


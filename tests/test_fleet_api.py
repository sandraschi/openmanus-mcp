"""Fleet + runner API smoke tests (no git, no real OpenManus)."""

from fastapi.testclient import TestClient

from openmanus_mcp.api.app import app

client = TestClient(app)


# ── fleet ─────────────────────────────────────────────────────────────────────


def test_fleet_catalog_ok() -> None:
    r = client.get("/api/v1/fleet/catalog")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert isinstance(data["members"], list)
    assert len(data["members"]) >= 1
    ids = {m["id"] for m in data["members"]}
    assert "pywinauto-mcp" in ids


def test_fleet_members_ok() -> None:
    r = client.get("/api/v1/fleet/members")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert isinstance(data["members"], dict)


# ── status includes runner_timeout_s ─────────────────────────────────────────


def test_status_has_runner_timeout() -> None:
    r = client.get("/api/v1/status")
    assert r.status_code == 200
    data = r.json()
    assert "runner_timeout_s" in data
    assert "job_store_max_completed" in data
    assert "async_jobs_stored" in data
    assert "async_jobs_pending" in data
    assert "ollama_base_url" in data
    assert "lmstudio_base_url" in data


# ── run endpoints: config error when OPENMANUS_ROOT unset ────────────────────


def test_run_sync_no_root() -> None:
    r = client.post("/api/v1/run", json={"prompt": "hello"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False
    assert "OPENMANUS_ROOT" in data["message"]


def test_run_async_no_root() -> None:
    r = client.post("/api/v1/run/async", json={"prompt": "hello"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False


def test_job_status_not_found() -> None:
    r = client.get("/api/v1/run/jobs/nonexistent-job-id-xyz")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "not_found"

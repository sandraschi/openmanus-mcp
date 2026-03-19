"""Supervisor heartbeat, schedules CRUD, connectors catalog."""

from fastapi.testclient import TestClient

from openmanus_mcp.api.app import app

client = TestClient(app)


def _clear_schedules() -> None:
    r = client.get("/api/v1/supervisor/schedules")
    assert r.status_code == 200
    for row in r.json():
        d = client.delete(f"/api/v1/supervisor/schedules/{row['id']}")
        assert d.status_code == 200


def test_supervisor_heartbeat() -> None:
    r = client.get("/api/v1/supervisor/heartbeat")
    assert r.status_code == 200
    data = r.json()
    assert "supervisor_enabled" in data
    assert "tick_count" in data
    assert data["supervisor_enabled"] is False


def test_status_includes_supervisor_fields() -> None:
    r = client.get("/api/v1/status")
    assert r.status_code == 200
    data = r.json()
    assert "supervisor_enabled" in data
    assert "supervisor_heartbeat" in data
    assert "supervisor_schedules" in data


def test_connectors_list() -> None:
    r = client.get("/api/v1/connectors")
    assert r.status_code == 200
    kinds = {c["kind"] for c in r.json()["connectors"]}
    assert kinds == {"email", "yahboom", "calibre"}


def test_connectors_one() -> None:
    r = client.get("/api/v1/connectors/email")
    assert r.status_code == 200
    assert r.json()["connector"]["kind"] == "email"


def test_connectors_404() -> None:
    r = client.get("/api/v1/connectors/nope")
    assert r.status_code == 404


def test_schedules_crud() -> None:
    try:
        r = client.post(
            "/api/v1/supervisor/schedules",
            json={
                "name": "t",
                "interval_s": 60,
                "prompt": "hello",
                "entry_point": "main.py",
                "enabled": True,
                "connector_kind": "email",
            },
        )
        assert r.status_code == 200
        row = r.json()
        sid = row["id"]
        assert row["connector_kind"] == "email"

        r2 = client.get("/api/v1/supervisor/schedules")
        assert r2.status_code == 200
        assert len(r2.json()) >= 1

        r3 = client.patch(f"/api/v1/supervisor/schedules/{sid}/enabled", json={"enabled": False})
        assert r3.status_code == 200
        assert r3.json()["enabled"] is False

        r4 = client.delete(f"/api/v1/supervisor/schedules/{sid}")
        assert r4.status_code == 200
    finally:
        _clear_schedules()

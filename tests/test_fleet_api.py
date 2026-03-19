"""Fleet API smoke tests (no git)."""

from fastapi.testclient import TestClient

from openmanus_mcp.api.app import app

client = TestClient(app)


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

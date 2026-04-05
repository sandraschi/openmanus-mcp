"""REST /api/v1/skills* endpoints."""

from fastapi.testclient import TestClient

from openmanus_mcp.api.app import app

client = TestClient(app)


def test_skills_list() -> None:
    r = client.get("/api/v1/skills")
    assert r.status_code == 200
    data = r.json()
    assert "skills" in data
    assert "estimated_index_chars" in data
    ids = {s["id"] for s in data["skills"]}
    assert "mcp-builder" in ids


def test_skills_one() -> None:
    r = client.get("/api/v1/skills/mcp-builder")
    assert r.status_code == 200
    data = r.json()
    assert "body" in data
    assert "mcp-builder" in data["body"].lower() or "MCP" in data["body"]


def test_skills_one_404() -> None:
    r = client.get("/api/v1/skills/does-not-exist-xyz")
    assert r.status_code == 404


def test_run_accepts_skill_ids_without_crash() -> None:
    """skill_ids are merged server-side; invalid OPENMANUS_ROOT still returns a clear error."""
    r = client.post(
        "/api/v1/run",
        json={"prompt": "task", "skill_ids": ["mcp-builder"], "entry_point": "main.py"},
    )
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is False
    assert "OPENMANUS_ROOT" in d["message"]

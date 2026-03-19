"""bridge_schema, dry-run, docs index, MCP manifest (no OpenManus subprocess)."""

from fastapi.testclient import TestClient

from openmanus_mcp.api.app import app
from openmanus_mcp.bridge_dry_run import dry_run_openmanus_bridge
from openmanus_mcp.bridge_schema import BRIDGE_OPERATION_NAMES, build_mcp_tools_manifest
from openmanus_mcp.settings import get_settings

client = TestClient(app)


def test_manifest_lists_all_bridge_operations() -> None:
    m = build_mcp_tools_manifest(get_settings())
    names = {op["name"] for op in m["operations"]}
    assert names == set(BRIDGE_OPERATION_NAMES)


def test_mcp_tools_endpoint() -> None:
    r = client.get("/api/v1/mcp/tools")
    assert r.status_code == 200
    data = r.json()
    assert data["stdio_tool"] == "openmanus_bridge"
    assert len(data["operations"]) == len(BRIDGE_OPERATION_NAMES)
    assert "mcp_dry_run" in data["rest_mirror"]
    assert "ollama_base_url" in data["glom_endpoints"]
    assert data["glom_endpoints"]["ollama_base_url"] == get_settings().ollama_base_url


def test_dry_run_unknown_operation() -> None:
    r = client.post("/api/v1/mcp/dry-run", json={"operation": "nope"})
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is False
    assert d["would_run_subprocess"] is False


def test_dry_run_status_ok() -> None:
    r = client.post("/api/v1/mcp/dry-run", json={"operation": "status"})
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is True
    assert d["would_run_subprocess"] is False


def test_dry_run_run_prompt_missing_prompt() -> None:
    r = client.post("/api/v1/mcp/dry-run", json={"operation": "run_prompt"})
    assert r.status_code == 200
    d = r.json()
    assert d["success"] is False


def test_dry_run_module_matches_api() -> None:
    d = dry_run_openmanus_bridge("validate")
    assert d["success"] is True


def test_docs_index_lists_md() -> None:
    r = client.get("/api/v1/docs")
    assert r.status_code == 200
    data = r.json()
    assert "documents" in data
    assert isinstance(data["documents"], list)


def test_runtime_settings() -> None:
    r = client.get("/api/v1/settings/runtime")
    assert r.status_code == 200
    data = r.json()
    assert "runner_timeout_s" in data
    assert "ollama_base_url" in data


def test_chat_personas() -> None:
    r = client.get("/api/v1/chat/personas")
    assert r.status_code == 200
    data = r.json()
    assert len(data["personas"]) >= 3


def test_system_gpu() -> None:
    r = client.get("/api/v1/system/gpu")
    assert r.status_code == 200
    data = r.json()
    assert "platform" in data
    assert "gpus" in data

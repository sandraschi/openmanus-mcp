"""Tests for the subprocess runner — no real OpenManus clone needed.

We use a tiny fake 'main.py' written to a tmp directory so tests run
in CI without any external deps.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from openmanus_mcp.runner import RunResult, _truncate, run_prompt

# ── helpers ──────────────────────────────────────────────────────────────────


def _write_fake_main(tmp_path: Path, body: str) -> Path:
    """Write a minimal fake main.py that echoes stdin prompt."""
    script = tmp_path / "main.py"
    script.write_text(textwrap.dedent(body), encoding="utf-8")
    return tmp_path


FAKE_ECHO = """\
import argparse
import sys
parser = argparse.ArgumentParser()
parser.add_argument("--prompt", default=None)
args = parser.parse_args()
if args.prompt is not None:
    prompt = args.prompt.strip()
else:
    prompt = sys.stdin.readline().strip()
print(f"Agent received: {prompt}")
sys.exit(0)
"""

FAKE_STDERR = """\
import argparse
import sys
parser = argparse.ArgumentParser()
parser.add_argument("--prompt", default=None)
args = parser.parse_args()
if args.prompt is not None:
    prompt = args.prompt.strip()
else:
    prompt = sys.stdin.readline().strip()
print(f"stdout: {prompt}")
print(f"stderr line", file=sys.stderr)
sys.exit(0)
"""

FAKE_NONZERO = """\
import argparse
import sys
parser = argparse.ArgumentParser()
parser.add_argument("--prompt", default=None)
args = parser.parse_args()
if args.prompt is None:
    sys.stdin.readline()
print("about to fail")
sys.exit(1)
"""

FAKE_SLOW = """\
import argparse
import sys
import time
parser = argparse.ArgumentParser()
parser.add_argument("--prompt", default=None)
args = parser.parse_args()
if args.prompt is None:
    sys.stdin.readline()
time.sleep(60)
print("done")
"""


# ── _truncate unit tests ──────────────────────────────────────────────────────


def test_truncate_short() -> None:
    text = "hello"
    out, trunc = _truncate(text, 100)
    assert out == text
    assert trunc is False


def test_truncate_long() -> None:
    text = "x" * 200
    out, trunc = _truncate(text, 100)
    assert trunc is True
    assert "TRUNCATED" in out
    assert len(out) < 300  # sanity — not exploding


# ── runner integration tests (real subprocess, fake script) ──────────────────


@pytest.mark.asyncio
async def test_run_prompt_echo(tmp_path: Path) -> None:
    root = _write_fake_main(tmp_path, FAKE_ECHO)
    result = await run_prompt(root, "hello world", timeout_s=15.0)
    assert isinstance(result, RunResult)
    assert result.success is True
    assert result.exit_code == 0
    assert "hello world" in result.stdout
    assert result.timed_out is False
    assert result.error is None


@pytest.mark.asyncio
async def test_run_prompt_captures_stderr(tmp_path: Path) -> None:
    root = _write_fake_main(tmp_path, FAKE_STDERR)
    result = await run_prompt(root, "ping", timeout_s=15.0)
    assert result.success is True
    assert "ping" in result.stdout
    assert "stderr line" in result.stderr


@pytest.mark.asyncio
async def test_run_prompt_nonzero_exit(tmp_path: Path) -> None:
    root = _write_fake_main(tmp_path, FAKE_NONZERO)
    result = await run_prompt(root, "ignored", timeout_s=15.0)
    assert result.success is False
    assert result.exit_code == 1
    assert result.timed_out is False


@pytest.mark.asyncio
async def test_run_prompt_timeout(tmp_path: Path) -> None:
    root = _write_fake_main(tmp_path, FAKE_SLOW)
    result = await run_prompt(root, "go", timeout_s=2.0)
    assert result.timed_out is True
    assert result.success is False
    assert "2.0s" in (result.error or "")


@pytest.mark.asyncio
async def test_run_prompt_missing_entrypoint(tmp_path: Path) -> None:
    # tmp_path has no main.py
    result = await run_prompt(tmp_path, "hello", timeout_s=5.0)
    assert result.success is False
    assert result.error is not None
    assert "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_run_prompt_run_flow_missing(tmp_path: Path) -> None:
    # tmp_path has no run_flow.py
    result = await run_prompt(tmp_path, "hello", entry_point="run_flow.py", timeout_s=5.0)
    assert result.success is False
    assert "not found" in (result.error or "").lower()


@pytest.mark.asyncio
async def test_run_prompt_multiline_uses_stdin_not_argv(tmp_path: Path) -> None:
    """Newline in prompt forces stdin path (run_flow never uses --prompt)."""
    body = """\
import sys
raw = sys.stdin.read()
print(raw.strip())
sys.exit(0)
"""
    root = _write_fake_main(tmp_path, body)
    result = await run_prompt(root, "line1\nline2", timeout_s=15.0)
    assert result.success is True
    assert "line1" in result.stdout and "line2" in result.stdout


# ── bridge integration (MCP tool level) ──────────────────────────────────────


@pytest.mark.asyncio
async def test_bridge_run_prompt_no_root() -> None:
    """run_prompt without OPENMANUS_ROOT returns config error, not a crash."""
    from openmanus_mcp.server import openmanus_bridge

    r = await openmanus_bridge("run_prompt", prompt="test")
    assert r["success"] is False
    assert "configuration" in r.get("error_type", "")


@pytest.mark.asyncio
async def test_bridge_run_prompt_empty_prompt() -> None:
    from openmanus_mcp.server import openmanus_bridge

    r = await openmanus_bridge("run_prompt", prompt="")
    assert r["success"] is False
    assert r["error_type"] == "invalid_argument"


@pytest.mark.asyncio
async def test_bridge_run_prompt_async_no_root() -> None:
    from openmanus_mcp.server import openmanus_bridge

    r = await openmanus_bridge("run_prompt_async", prompt="test")
    assert r["success"] is False


@pytest.mark.asyncio
async def test_bridge_job_status_unknown() -> None:
    from openmanus_mcp.server import openmanus_bridge

    r = await openmanus_bridge("job_status", job_id="does-not-exist-xyz")
    assert r["success"] is False
    assert r["error_type"] == "not_found"


@pytest.mark.asyncio
async def test_bridge_job_status_missing_id() -> None:
    from openmanus_mcp.server import openmanus_bridge

    r = await openmanus_bridge("job_status")
    assert r["success"] is False
    assert r["error_type"] == "invalid_argument"

"""Subprocess runner for FoundationAgents/OpenManus.

OpenManus **main.py** accepts ``--prompt`` (CLI) or falls back to ``input()``;
**run_flow.py** uses ``input()`` only. For **main.py** with a **single-line**
prompt (no newlines), we pass ``--prompt`` and **DEVNULL** stdin to avoid
relying on pipe semantics where unnecessary. Otherwise we write the prompt
line to stdin (``input()`` path).

Supported entry points:
  - main.py     (Manus general-purpose agent)
  - run_flow.py (multi-agent DataAnalysis + Manus)

Design constraints:
  - No pseudo-tty — OpenManus works fine with piped stdio.
  - asyncio.create_subprocess_exec for non-blocking line streaming.
  - Caller can pass a timeout; default is configurable in Settings.
  - Hard cap: MAX_OUTPUT_CHARS to prevent MCP response blowout.
"""

from __future__ import annotations

import asyncio
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

MAX_OUTPUT_CHARS = 40_000  # total stdout+stderr cap before truncation
_SENTINEL = object()

EntryPoint = Literal["main.py", "run_flow.py"]


@dataclass
class RunResult:
    """Structured result from one OpenManus subprocess run."""

    success: bool
    entry_point: str
    prompt: str
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    execution_time_ms: float
    truncated: bool = False
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "entry_point": self.entry_point,
            "prompt": self.prompt,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "truncated": self.truncated,
            "error": self.error,
            "execution_time_ms": round(self.execution_time_ms, 2),
        }


def _python_for_root(openmanus_root: Path) -> str:
    """Return the Python interpreter to use for this OpenManus clone.

    Prefers the venv inside the clone (uv-created), falls back to sys.executable.
    On Windows: .venv/Scripts/python.exe
    On Unix:    .venv/bin/python
    """
    candidates = [
        openmanus_root / ".venv" / "Scripts" / "python.exe",  # Windows uv
        openmanus_root / ".venv" / "bin" / "python",  # Unix uv
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    return sys.executable


def _truncate(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    half = limit // 2
    return (
        text[:half]
        + f"\n... [TRUNCATED — {len(text)} chars total, showing first+last {half}] ...\n"
        + text[-half:],
        True,
    )


def _extract_last_step_line(stdout_text: str) -> str | None:
    """Return the final `Step N:` line from OpenManus stdout."""
    step_lines = re.findall(r"^Step\s+\d+:\s+.*$", stdout_text, flags=re.MULTILINE)
    return step_lines[-1] if step_lines else None


def _quality_gate(success: bool, stdout_text: str, stderr_text: str) -> tuple[bool, str | None]:
    """Reject false-positive success from known non-productive OpenManus outcomes."""
    if not success:
        return success, None

    combined = f"{stdout_text}\n{stderr_text}".lower()
    last_step = (_extract_last_step_line(stdout_text) or "").lower()

    if "terminated: reached max steps" in combined:
        return False, "OpenManus terminated at max steps without reliable completion"
    if "error_loop_guard" in last_step and "step" in last_step:
        return False, "OpenManus loop guard triggered before final completion"
    if "error_loop_guard" in combined and "step" not in last_step:
        return False, "OpenManus loop guard triggered"

    return True, None


async def run_prompt(
    openmanus_root: Path,
    prompt: str,
    entry_point: EntryPoint = "main.py",
    timeout_s: float = 300.0,
) -> RunResult:
    """Run OpenManus with *prompt*; see module docstring for argv vs stdin.

    stdout and stderr are read concurrently to avoid deadlock.
    """
    t0 = time.perf_counter()
    script = openmanus_root / entry_point
    if not script.is_file():
        return RunResult(
            success=False,
            entry_point=entry_point,
            prompt=prompt,
            stdout="",
            stderr="",
            exit_code=None,
            timed_out=False,
            execution_time_ms=(time.perf_counter() - t0) * 1000,
            error=f"Entry point not found: {script}",
        )

    python = _python_for_root(openmanus_root)
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    exit_code: int | None = None
    timed_out = False
    proc_error: str | None = None

    use_argv_prompt = entry_point == "main.py" and "\n" not in prompt and "\r" not in prompt

    try:
        if use_argv_prompt:
            proc = await asyncio.create_subprocess_exec(
                python,
                str(script),
                "--prompt",
                prompt,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(openmanus_root),
            )
        else:
            proc = await asyncio.create_subprocess_exec(
                python,
                str(script),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(openmanus_root),
            )
            assert proc.stdin is not None
            proc.stdin.write((prompt + "\n").encode("utf-8", errors="replace"))
            await proc.stdin.drain()
            proc.stdin.close()

        async def drain_stream(stream: asyncio.StreamReader, buf: list[str]) -> None:
            while True:
                line = await stream.readline()
                if not line:
                    break
                buf.append(line.decode("utf-8", errors="replace"))

        assert proc.stdout is not None
        assert proc.stderr is not None

        try:
            await asyncio.wait_for(
                asyncio.gather(
                    drain_stream(proc.stdout, stdout_lines),
                    drain_stream(proc.stderr, stderr_lines),
                    proc.wait(),
                ),
                timeout=timeout_s,
            )
            exit_code = proc.returncode
        except TimeoutError:
            timed_out = True
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
            exit_code = proc.returncode

    except FileNotFoundError as exc:
        proc_error = f"Python interpreter not found: {exc}"
    except Exception as exc:
        proc_error = f"Subprocess error: {exc}"

    stdout_raw = "".join(stdout_lines)
    stderr_raw = "".join(stderr_lines)
    combined_len = len(stdout_raw) + len(stderr_raw)
    truncated = False

    if combined_len > MAX_OUTPUT_CHARS:
        # Allocate cap proportionally
        stdout_cap = int(MAX_OUTPUT_CHARS * len(stdout_raw) / max(combined_len, 1))
        stderr_cap = MAX_OUTPUT_CHARS - stdout_cap
        stdout_raw, t1 = _truncate(stdout_raw, stdout_cap)
        stderr_raw, t2 = _truncate(stderr_raw, stderr_cap)
        truncated = t1 or t2

    elapsed_ms = (time.perf_counter() - t0) * 1000
    success = proc_error is None and not timed_out and exit_code == 0
    quality_error: str | None = None
    success, quality_error = _quality_gate(success, stdout_raw, stderr_raw)
    if quality_error and proc_error is None:
        proc_error = quality_error

    return RunResult(
        success=success,
        entry_point=entry_point,
        prompt=prompt,
        stdout=stdout_raw,
        stderr=stderr_raw,
        exit_code=exit_code,
        timed_out=timed_out,
        execution_time_ms=elapsed_ms,
        truncated=truncated,
        error=proc_error or (f"Timed out after {timeout_s}s" if timed_out else None),
    )

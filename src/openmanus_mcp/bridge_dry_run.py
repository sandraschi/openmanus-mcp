"""Validate openmanus_bridge calls without starting a subprocess."""

from __future__ import annotations

import time
from typing import Any

from openmanus_mcp.bridge_schema import BRIDGE_OPERATION_NAMES
from openmanus_mcp.openmanus_detect import describe_openmanus
from openmanus_mcp.settings import get_settings


def dry_run_openmanus_bridge(
    operation: str,
    prompt: str | None = None,
    entry_point: str = "main.py",
    timeout_s: float | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Mirror server-side validation for openmanus_bridge; never runs OpenManus."""
    t0 = time.perf_counter()
    settings = get_settings()
    info = describe_openmanus(settings.openmanus_root)
    op = operation.strip().lower()
    checks: list[dict[str, Any]] = []

    checks.append({"check": "operation_known", "ok": op in BRIDGE_OPERATION_NAMES, "operation": op})
    if op not in BRIDGE_OPERATION_NAMES:
        return {
            "success": False,
            "would_run_subprocess": False,
            "checks": checks,
            "error_type": "invalid_argument",
            "message": f"Unknown operation {operation!r}",
            "recovery_options": [
                f"Use one of: {', '.join(BRIDGE_OPERATION_NAMES)}",
            ],
            "execution_time_ms": round((time.perf_counter() - t0) * 1000, 2),
        }

    if op in ("run_prompt", "run_prompt_async"):
        p_ok = bool(prompt and prompt.strip())
        checks.append({"check": "prompt_non_empty", "ok": p_ok})
        if not p_ok:
            return {
                "success": False,
                "would_run_subprocess": False,
                "checks": checks,
                "error_type": "invalid_argument",
                "message": "prompt is required and must be non-empty",
                "execution_time_ms": round((time.perf_counter() - t0) * 1000, 2),
            }

    if op == "job_status":
        j_ok = bool(job_id and job_id.strip())
        checks.append({"check": "job_id_present", "ok": j_ok})
        if not j_ok:
            return {
                "success": False,
                "would_run_subprocess": False,
                "checks": checks,
                "error_type": "invalid_argument",
                "message": "job_id is required for job_status",
                "execution_time_ms": round((time.perf_counter() - t0) * 1000, 2),
            }

    ep = "run_flow.py" if entry_point == "run_flow.py" else "main.py"
    if ep not in ("main.py", "run_flow.py"):
        checks.append({"check": "entry_point_enum", "ok": False, "entry_point": entry_point})
        return {
            "success": False,
            "would_run_subprocess": False,
            "checks": checks,
            "error_type": "invalid_argument",
            "message": 'entry_point must be "main.py" or "run_flow.py"',
            "execution_time_ms": round((time.perf_counter() - t0) * 1000, 2),
        }
    checks.append({"check": "entry_point_enum", "ok": True, "entry_point": ep})

    root_ok = info is not None and info.looks_valid
    checks.append(
        {"check": "openmanus_root_valid", "ok": root_ok, "path": str(info.root) if info else None}
    )

    if op in ("run_prompt", "run_prompt_async") and not root_ok:
        return {
            "success": False,
            "would_run_subprocess": False,
            "checks": checks,
            "error_type": "configuration",
            "message": "OPENMANUS_ROOT is not set or invalid — fix before running",
            "recovery_options": [
                "Set OPENMANUS_ROOT in .env to a full OpenManus clone",
                "Run operation=validate via MCP for details",
            ],
            "execution_time_ms": round((time.perf_counter() - t0) * 1000, 2),
        }

    t_out = timeout_s if timeout_s is not None else settings.runner_timeout_s
    checks.append(
        {
            "check": "effective_timeout_s",
            "ok": t_out > 0,
            "timeout_s": t_out,
        }
    )

    would_subprocess = op in ("run_prompt", "run_prompt_async")
    return {
        "success": True,
        "would_run_subprocess": would_subprocess,
        "checks": checks,
        "message": (
            "Dry-run OK — subprocess would start next."
            if would_subprocess
            else "Dry-run OK — no subprocess for this operation."
        ),
        "preview": {
            "operation": op,
            "entry_point": ep,
            "timeout_s": t_out,
            "openmanus_root": str(info.root) if info else None,
        },
        "execution_time_ms": round((time.perf_counter() - t0) * 1000, 2),
    }
def main() -> None:
    import json
    import sys

    op = sys.argv[1] if len(sys.argv) > 1 else "validate"
    res = dry_run_openmanus_bridge(op)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()

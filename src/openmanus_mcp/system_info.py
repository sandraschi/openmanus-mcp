"""Best-effort GPU / display adapter discovery (no third-party drivers required)."""

from __future__ import annotations

import platform
import re
import subprocess
import sys
from typing import Any


def _list_gpus_windows() -> list[dict[str, Any]]:
    """Windows-specific GPU discovery via CIM/WMI."""
    gpus: list[dict[str, Any]] = []
    try:
        proc = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-STA",
                "-Command",
                "Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name }",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        for line in (proc.stdout or "").splitlines():
            name = line.strip()
            if name:
                gpus.append({"name": name, "source": "Win32_VideoController"})
        if proc.returncode != 0 and not gpus:
            gpus.append(
                {
                    "source": "Win32_VideoController",
                    "stderr": (proc.stderr or "")[:500],
                    "returncode": proc.returncode,
                }
            )
    except Exception as e:
        gpus.append({"error": str(e), "source": "windows_exception"})
    return gpus


def _list_gpus_darwin() -> list[dict[str, Any]]:
    """macOS-specific GPU discovery via system_profiler."""
    gpus: list[dict[str, Any]] = []
    try:
        proc = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            timeout=25,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        text = proc.stdout or ""
        for m in re.finditer(r"^\s*Chipset Model:\s*(.+)$", text, re.MULTILINE):
            gpus.append({"name": m.group(1).strip(), "source": "system_profiler"})
        if not gpus and text.strip():
            gpus.append({"raw_excerpt": text[:800], "source": "system_profiler"})
    except Exception as e:
        gpus.append({"error": str(e), "source": "darwin_exception"})
    return gpus


def _list_gpus_linux() -> list[dict[str, Any]]:
    """Linux GPU discovery via nvidia-smi."""
    gpus: list[dict[str, Any]] = []
    try:
        proc = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=12,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if proc.returncode == 0:
            for line in (proc.stdout or "").splitlines():
                n = line.strip()
                if n:
                    gpus.append({"name": n, "source": "nvidia-smi"})
    except (FileNotFoundError, Exception) as e:
        # FileNotFoundError is expected if no nvidia drivers
        if not isinstance(e, FileNotFoundError):
            gpus.append({"error": str(e), "source": "linux_exception"})
    return gpus


def list_gpus() -> dict[str, Any]:
    """Return structured GPU info for the current machine."""
    plat = platform.system()
    gpus: list[dict[str, Any]] = []

    if sys.platform == "win32":
        gpus = _list_gpus_windows()
    elif sys.platform == "darwin":
        gpus = _list_gpus_darwin()
    else:
        gpus = _list_gpus_linux()

    targets = ("RTX", "RADEON", "ARC", "APPLE M", "MIRO", "TESLA", "A100", "H100")
    suggest_local_llm = any(
        any(x in (g.get("name") or "").upper() for x in targets) for g in gpus
    )

    return {
        "platform": plat,
        "gpus": gpus,
        "suggest_local_llm": suggest_local_llm,
    }

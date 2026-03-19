"""Best-effort GPU / display adapter discovery (no third-party drivers required)."""

from __future__ import annotations

import platform
import re
import subprocess
import sys
from typing import Any


def list_gpus() -> dict[str, Any]:
    """Return structured GPU info for the current machine."""
    plat = platform.system()
    gpus: list[dict[str, Any]] = []

    if sys.platform == "win32":
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
            return {"platform": plat, "gpus": [], "error": str(e), "source": "windows"}

    elif sys.platform == "darwin":
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
            return {"platform": plat, "gpus": [], "error": str(e), "source": "darwin"}

    else:
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
        except FileNotFoundError:
            pass
        except Exception as e:
            return {"platform": plat, "gpus": gpus, "error": str(e), "source": "linux"}

    suggest_local_llm = False
    for g in gpus:
        name = (g.get("name") or "").upper()
        if any(x in name for x in ("RTX", "RADEON", "ARC", "APPLE M", "MIRO", "TESLA", "A100", "H100")):
            suggest_local_llm = True
            break

    return {
        "platform": plat,
        "gpus": gpus,
        "suggest_local_llm": suggest_local_llm,
    }

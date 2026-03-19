"""Adaptive OpenManus run concurrency control.

Cap is derived from CPU cores, system RAM, and GPU VRAM/speed hints.
"""

from __future__ import annotations

import asyncio
import os
import platform
import re
import subprocess
from dataclasses import dataclass


def _ram_gb() -> float:
    try:
        if os.name == "nt":
            proc = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-STA",
                    "-Command",
                    "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,2)",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            val = (proc.stdout or "").strip()
            return float(val) if val else 0.0
        if platform.system() == "Linux":
            txt = ""
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                txt = f.read()
            m = re.search(r"MemTotal:\s+(\d+)\s+kB", txt)
            if not m:
                return 0.0
            return int(m.group(1)) / (1024 * 1024)
    except Exception:
        return 0.0
    return 0.0


def _gpu_hint() -> tuple[float, int]:
    """Return (best_vram_gb, gpu_speed_score 0..3)."""
    best_vram = 0.0
    speed_score = 0

    try:
        if os.name == "nt":
            proc = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-STA",
                    "-Command",
                    "Get-CimInstance Win32_VideoController | ForEach-Object { \"$($_.Name)|$($_.AdapterRAM)\" }",
                ],
                capture_output=True,
                text=True,
                timeout=15,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            for line in (proc.stdout or "").splitlines():
                name, _, ram = line.partition("|")
                n = name.strip().upper()
                try:
                    vram = int((ram or "0").strip()) / (1024**3)
                except Exception:
                    vram = 0.0
                best_vram = max(best_vram, vram)
                if any(x in n for x in ("H100", "A100", "4090", "5090", "RTX 6000", "MI300")):
                    speed_score = max(speed_score, 3)
                elif any(x in n for x in ("RTX", "RX 7", "RX 8", "ARC")):
                    speed_score = max(speed_score, 2)
                elif any(x in n for x in ("GTX", "RADEON", "APPLE M")):
                    speed_score = max(speed_score, 1)
        else:
            proc = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if proc.returncode == 0:
                for line in (proc.stdout or "").splitlines():
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) < 2:
                        continue
                    n = parts[0].upper()
                    try:
                        vram = float(parts[1]) / 1024.0
                    except Exception:
                        vram = 0.0
                    best_vram = max(best_vram, vram)
                    if any(x in n for x in ("H100", "A100", "4090", "5090", "RTX 6000", "MI300")):
                        speed_score = max(speed_score, 3)
                    elif "RTX" in n:
                        speed_score = max(speed_score, 2)
                    else:
                        speed_score = max(speed_score, 1)
    except Exception:
        return (best_vram, speed_score)

    return (best_vram, speed_score)


def _derive_cap() -> tuple[int, dict[str, float | int]]:
    cores = max(1, int(os.cpu_count() or 1))
    ram = _ram_gb()
    vram, gpu_speed = _gpu_hint()

    cpu_cap = max(1, cores // 4)
    ram_cap = max(1, int(ram // 6)) if ram > 0 else 1

    # GPU cap is conservative; large models tend to serialize anyway.
    if vram >= 20:
        gpu_cap = 3 if gpu_speed >= 2 else 2
    elif vram >= 12:
        gpu_cap = 2
    elif vram >= 6:
        gpu_cap = 1
    else:
        gpu_cap = 1

    cap = min(max(1, cpu_cap), max(1, ram_cap), max(1, gpu_cap))
    cap = min(cap, 8)  # hard safety upper bound
    return cap, {
        "cores": cores,
        "ram_gb": round(ram, 2),
        "gpu_vram_gb": round(vram, 2),
        "gpu_speed_score": gpu_speed,
        "cpu_cap": cpu_cap,
        "ram_cap": ram_cap,
        "gpu_cap": gpu_cap,
    }


@dataclass
class AdaptiveLimiter:
    cap: int
    metrics: dict[str, float | int]
    _sem: asyncio.Semaphore
    _active: int = 0
    _lock: asyncio.Lock | None = None

    @classmethod
    def create(cls) -> "AdaptiveLimiter":
        cap, metrics = _derive_cap()
        return cls(cap=cap, metrics=metrics, _sem=asyncio.Semaphore(cap), _lock=asyncio.Lock())

    async def acquire(self) -> None:
        await self._sem.acquire()
        assert self._lock is not None
        async with self._lock:
            self._active += 1

    async def release(self) -> None:
        assert self._lock is not None
        async with self._lock:
            self._active = max(0, self._active - 1)
        self._sem.release()

    @property
    def active(self) -> int:
        return self._active

    @property
    def available(self) -> int:
        return max(0, self.cap - self._active)


_api_limiter: AdaptiveLimiter | None = None


def api_run_limiter() -> AdaptiveLimiter:
    global _api_limiter
    if _api_limiter is None:
        _api_limiter = AdaptiveLimiter.create()
    return _api_limiter

"""Concurrency controls for OpenManus MCP server – adaptive run limiting and GPU detection."""

from __future__ import annotations

import asyncio
import platform
import subprocess
import threading
from dataclasses import dataclass
from typing import Any

import structlog

log = structlog.get_logger(__name__)

# --- Resource Discovery ------------------------------------------------------


def _mem_total_gb() -> float:
    """Return total physical RAM in GB (Windows-optimized)."""
    if platform.system() != "Windows":
        return 16.0  # Safe fallback for Linux/macOS in this bridge
    try:
        # PowerShell command wrapped to fit line limit
        cmd = ["[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,2)"]
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-STA", "-Command", *cmd],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            return float(res.stdout.strip())
    except Exception as exc:
        log.debug("mem_total_gb_failed", exc=str(exc))
    return 8.0


def _parse_gpu_line(line: str) -> tuple[str, float]:
    """Parse 'Name|Bytes' line from PowerShell."""
    if "|" not in line:
        return "", 0.0
    name, raw_bytes = line.split("|", 1)
    try:
        gb = float(raw_bytes) / (1024**3)
        return name, gb
    except (ValueError, TypeError):
        return name, 0.0


def _gpu_hint() -> tuple[float, int]:
    """Return (best_vram_gb, gpu_speed_score 0..3)."""
    best_vram = 0.0
    if platform.system() != "Windows":
        return 0.0, 0
    try:
        # PowerShell command for GPU info wrapped to fit line limit
        raw_cmd = (
            "Get-CimInstance Win32_VideoController | "
            "ForEach-Object { \"$($_.Name)|$($_.AdapterRAM)\" }"
        )
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-STA", "-Command", raw_cmd],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                name, gb = _parse_gpu_line(line)
                best_vram = max(best_vram, gb)
                # 4090/3090 detect (score 3)
                if any(x in name for x in ("4090", "3090", "A6000")):
                    return gb, 3
    except Exception as exc:
        log.debug("gpu_hint_failed", exc=str(exc))

    # PLR0911 reduction: use a single return point for scores 0-2
    score = 0
    if best_vram >= 23.0:
        score = 3
    elif best_vram >= 11.0:
        score = 2
    elif best_vram >= 7.0:
        score = 1

    return best_vram, score


# --- Limit Logic -----------------------------------------------------------


@dataclass(frozen=True)
class LimitMetrics:
    total_mem_gb: float
    best_vram_gb: float
    gpu_score: int
    cap: int


class AdaptiveLimiter:
    """Semi-intelligent run limiter based on hardware detected at startup."""

    def __init__(self, metrics: LimitMetrics):
        self._metrics = metrics
        self._cap = metrics.cap
        self._active = 0
        self._sem = asyncio.Semaphore(self._cap)
        self._lock: asyncio.Lock | None = None

    @classmethod
    def create(cls) -> AdaptiveLimiter:
        """Analyze hardware and return a tuned limiter."""
        mem = _mem_total_gb()
        vram, score = _gpu_hint()

        # baseline 1 concurrent; +1 for 32GB RAM; +1 for High GPU; max 3
        # (OpenManus sub-agents consume significant resources)
        cap = 1
        if mem >= 30.0:
            cap += 1
        if score >= 2:
            cap += 1

        metrics = LimitMetrics(total_mem_gb=mem, best_vram_gb=vram, gpu_score=score, cap=cap)
        log.info("adaptive_limiter_init", cap=cap, mem=mem, vram=vram)
        return cls(metrics)

    @property
    def cap(self) -> int:
        return self._cap

    @property
    def metrics(self) -> dict[str, Any]:
        return {
            "total_mem_gb": self._metrics.total_mem_gb,
            "best_vram_gb": self._metrics.best_vram_gb,
            "gpu_score": self._metrics.gpu_score,
            "cap": self._cap,
        }

    @property
    def active(self) -> int:
        return self._active

    @property
    def available(self) -> int:
        return max(0, self._cap - self._active)

    async def _ensure_lock(self) -> None:
        if self._lock is None:
            self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        await self._sem.acquire()
        await self._ensure_lock()
        if self._lock:
            async with self._lock:
                self._active += 1

    async def release(self) -> None:
        await self._ensure_lock()
        if self._lock:
            async with self._lock:
                self._active = max(0, self._active - 1)
        self._sem.release()


class _LimiterState:
    """Internal singleton holder for the API limiter."""

    def __init__(self):
        self._instance: AdaptiveLimiter | None = None
        self._mutex = threading.Lock()

    def get_limiter(self) -> AdaptiveLimiter:
        if self._instance is None:
            with self._mutex:
                if self._instance is None:
                    self._instance = AdaptiveLimiter.create()
        return self._instance


_STATE = _LimiterState()


def api_run_limiter() -> AdaptiveLimiter:
    """Return the global (singleton) run limiter."""
    return _STATE.get_limiter()

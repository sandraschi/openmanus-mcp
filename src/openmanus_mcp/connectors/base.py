"""Connector abstraction: fleet MCPs / external channels (OpenClaw-style)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ConnectorKind(StrEnum):
    """Built-in connector identifiers (extend via registry)."""

    EMAIL = "email"
    YAHBOOM = "yahboom"
    CALIBRE = "calibre"


@dataclass(frozen=True, slots=True)
class ConnectorInfo:
    """Static metadata for UI and supervisor prompts."""

    kind: ConnectorKind
    title: str
    summary: str
    mcp_hint: str
    proactive_prompt: str
    capabilities: tuple[str, ...]

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "title": self.title,
            "summary": self.summary,
            "mcp_hint": self.mcp_hint,
            "proactive_prompt": self.proactive_prompt,
            "capabilities": list(self.capabilities),
        }

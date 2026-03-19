"""Persona system prompts for SOTA Chat (WEBAPP_STANDARDS §4). Single backend source."""

from __future__ import annotations

from typing import Any, Literal

PersonaId = Literal["reductionist", "debugger", "explainer"]

PERSONAS: list[dict[str, Any]] = [
    {
        "id": "reductionist",
        "label": "Reductionist (Sandra)",
        "description": "Industrial, technically exhaustive answers.",
    },
    {
        "id": "debugger",
        "label": "Debugger",
        "description": "Trace-focused; edge cases and failure modes.",
    },
    {
        "id": "explainer",
        "label": "Explainer",
        "description": "Architecture, patterns, and concepts.",
    },
]


def persona_system_prompt(persona: str, *, intent: str) -> str:
    """Build system message for chat or refine."""
    pid = persona.strip().lower()
    prompts = {
        "reductionist": (
            "You are a reductionist technical assistant. Be direct, exhaustive, and precise. "
            "Prefer facts, steps, and explicit trade-offs over filler."
        ),
        "debugger": (
            "You are a debugging-oriented assistant. Surface edge cases, invariants, "
            "likely failure points, and concrete checks."
        ),
        "explainer": (
            "You are an explainer focused on architecture, patterns, and mental models. "
            "Use structure (headings mentally) but output plain text unless asked."
        ),
    }
    base = prompts.get(pid, prompts["reductionist"])

    if intent == "refine":
        return (
            f"{base}\n\nYour only task: rewrite the user's draft prompt into a clearer, "
            "more effective instruction for a coding/agent assistant. Output only the improved "
            "prompt text, no preamble."
        )
    return (
        f"{base}\n\nYou answer in the chat UI. Keep responses focused. "
        "If the user supplies page context, treat it as background only."
    )


def list_personas_public() -> list[dict[str, Any]]:
    """Subset safe to expose to the web client (no hidden prompt text if we want — we expose labels)."""
    return [{"id": p["id"], "label": p["label"], "description": p["description"]} for p in PERSONAS]

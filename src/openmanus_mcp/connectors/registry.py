"""Registry of built-in connectors (no live MCP calls here — wiring is client-side)."""

from __future__ import annotations

from openmanus_mcp.connectors.base import ConnectorInfo, ConnectorKind

_BUILTIN: dict[ConnectorKind, ConnectorInfo] = {
    ConnectorKind.EMAIL: ConnectorInfo(
        kind=ConnectorKind.EMAIL,
        title="Email / inbox",
        summary="Inbox triage, drafts, and weeding via email-mcp (IMAP/SMTP).",
        mcp_hint=("email-mcp — use when the user has Cursor MCP `emailops` or stdio email server configured."),
        proactive_prompt=(
            "Proactive inbox weeding: list unread or stale threads, "
            "propose archive/delete rules with safety checks, "
            "draft 3 reply templates for the highest-signal threads, "
            "and output a 5-minute execution checklist. "
            "Assume email MCP tools are available; if not, say what to enable."
        ),
        capabilities=(
            "inbox_list",
            "thread_summarize",
            "draft_reply",
            "label_or_move",
        ),
    ),
    ConnectorKind.YAHBOOM: ConnectorInfo(
        kind=ConnectorKind.YAHBOOM,
        title="Yahboom robot",
        summary="Patrol, sensors, and motion via yahboom-mcp when connected.",
        mcp_hint="yahboom-mcp — security patrol / GPIO / camera workflows.",
        proactive_prompt=(
            "Security patrol plan for a Yahboom-class rover: "
            "define a safe patrol loop (start/stop, obstacle backoff, log anomalies), "
            "suggest sensor checks (battery, distance), "
            "and a short incident script if motion is detected. "
            "Reference MCP robot tools if available."
        ),
        capabilities=(
            "patrol_route",
            "sensor_read",
            "motor_guard",
            "event_log",
        ),
    ),
    ConnectorKind.CALIBRE: ConnectorInfo(
        kind=ConnectorKind.CALIBRE,
        title="Calibre library",
        summary="Metadata, shelves, and RAG-style book discovery via calibre-mcp.",
        mcp_hint="calibre-mcp / CalibreMCP — library query and recommendations.",
        proactive_prompt=(
            "Calibre book recommendations: infer reading taste from recent shelves or tags "
            "(or ask for 3 favorite titles), query the library for gaps, "
            "propose 5 next reads with one-line rationale each, "
            "and optional series completion order. Use Calibre MCP tools when present."
        ),
        capabilities=(
            "library_query",
            "metadata_search",
            "series_order",
            "reading_list",
        ),
    ),
}


def list_connectors() -> list[dict[str, object]]:
    """Public list for REST /api/v1/connectors."""
    return [c.to_public_dict() for c in _BUILTIN.values()]


def get_connector(kind: str) -> dict[str, object] | None:
    try:
        k = ConnectorKind(kind)
    except ValueError:
        return None
    return _BUILTIN[k].to_public_dict()

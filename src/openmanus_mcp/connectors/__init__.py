"""Connector registry for comms / robots / media fleet MCPs."""

from openmanus_mcp.connectors.base import ConnectorInfo, ConnectorKind
from openmanus_mcp.connectors.registry import get_connector, list_connectors

__all__ = ["ConnectorInfo", "ConnectorKind", "get_connector", "list_connectors"]

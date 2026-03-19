"""openmanus-mcp: FastMCP 3.1 wrapper for FoundationAgents OpenManus."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("openmanus-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

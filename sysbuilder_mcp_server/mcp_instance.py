"""Sysbuilder MCP Server FastMCP singleton."""
from __future__ import annotations

from sysbuilder_mcp_server.path_config import get_output_root, get_resources_root, get_workspace_root

try:
    from mcp.server.fastmcp import FastMCP

    _FASTMCP_AVAILABLE = True
except ImportError:
    _FASTMCP_AVAILABLE = False

    class FastMCP:  # type: ignore[override]
        def __init__(self, _name: str, instructions: str | None = None) -> None:
            self._name = _name
            self.instructions = instructions

        def tool(self):
            def _decorator(func):
                return func

            return _decorator

        def run(self) -> None:
            raise RuntimeError("FastMCP not installed")


_INSTRUCTIONS = f"""
You are using the Sysbuilder MCP server.

Path conventions:
- Workspace root: {get_workspace_root()}
- Resources root: {get_resources_root()}
- Output root: {get_output_root()}

Hard constraints:
- For modeling tasks, generate a complete UTF-8 Python modeling script first, then call the run_script tool to execute it.
- Use GenerateModelicaSimulationFramework for Modelica framework generation.
- Use GenGeometricParam for geometric parameter document generation.
""".strip()


mcp = FastMCP("sysbuilder_mcp", instructions=_INSTRUCTIONS)

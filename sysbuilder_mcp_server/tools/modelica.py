"""Sysbuilder Modelica framework MCP tool."""
from __future__ import annotations

from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.core import GenerateModelicaSimulationFramework
from sysbuilder_mcp_server.tools.common import _json, capture_python_output, ensure_sysbuilder_session


@mcp.tool()
def generate_modelica_framework(
    full_name: str,
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    调用 Sysbuilder API `GenerateModelicaSimulationFramework` 生成 Modelica 仿真框架。

    `full_name` 应传入目标元素的完整名称。
    """
    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "generate_modelica_framework",
                "error": "Failed to start or connect Sysbuilder.",
                "session": session,
            }
        )

    with capture_python_output() as (buf_out, buf_err):
        result = GenerateModelicaSimulationFramework(full_name)
    return _json(
        {
            "ok": bool(result),
            "tool": "generate_modelica_framework",
            "full_name": full_name,
            "api": "GenerateModelicaSimulationFramework",
            "result": result,
            "session": session,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )

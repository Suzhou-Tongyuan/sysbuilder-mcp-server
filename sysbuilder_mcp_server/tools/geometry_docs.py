"""Sysbuilder geometric parameter document MCP tool."""
from __future__ import annotations

from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.core import GenGeometricParam
from sysbuilder_mcp_server.tools.common import (
    _json,
    capture_python_output,
    ensure_sysbuilder_session,
    resolve_output_path,
)


@mcp.tool()
def generate_geometric_param_doc(
    diagram_full_name: str,
    module_name: str,
    output_path: str = "",
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    调用 Sysbuilder API `GenGeometricParam` 生成几何参数 Markdown 文档。

    `diagram_full_name` 为模块定义图全名，`module_name` 为图中目标模块名称。
    """
    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "generate_geometric_param_doc",
                "error": "Failed to start or connect Sysbuilder.",
                "session": session,
            }
        )

    resolved_output = resolve_output_path(output_path, default_name="几何参数文档.md")
    with capture_python_output() as (buf_out, buf_err):
        result = GenGeometricParam(
            diagramFullName=diagram_full_name,
            moduleName=module_name,
            outputPath=str(resolved_output),
        )
    return _json(
        {
            "ok": bool(result),
            "tool": "generate_geometric_param_doc",
            "diagram_full_name": diagram_full_name,
            "module_name": module_name,
            "output_path": str(resolved_output),
            "api": "GenGeometricParam",
            "result": result,
            "session": session,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )

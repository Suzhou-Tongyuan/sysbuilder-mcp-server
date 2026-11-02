"""Sysbuilder semantic JSON export MCP tool."""
from __future__ import annotations

from mworks.sysbuilder import ExportSemanticJson
from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.tools.common import (
    _json,
    capture_python_output,
    ensure_sysbuilder_session,
    resolve_output_path,
)


@mcp.tool()
def export_semantic_json(
    output_path: str = "",
    full_name: str = "",
    include_hidden: bool = False,
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    调用 Sysbuilder API `ExportSemanticJson` 导出 SysML2 语义树 JSON 文件。

    `full_name` 为空时导出全工程，非空时导出指定元素及其 owned 子树。
    """
    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "export_semantic_json",
                "error": "Failed to start or connect Sysbuilder.",
                "session": session,
            }
        )

    resolved_output = resolve_output_path(output_path, default_name="semantic_tree.json")
    with capture_python_output() as (buf_out, buf_err):
        result = ExportSemanticJson(
            path=str(resolved_output),
            fullName=full_name,
            includeHidden=include_hidden,
        )

    return _json(
        {
            "ok": bool(result),
            "tool": "export_semantic_json",
            "output_path": str(resolved_output),
            "full_name": full_name,
            "include_hidden": include_hidden,
            "api": "ExportSemanticJson",
            "result": result,
            "session": session,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )

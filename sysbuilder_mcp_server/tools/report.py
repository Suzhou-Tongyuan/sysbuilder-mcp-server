"""Sysbuilder system design report MCP tool."""
from __future__ import annotations

from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.core import GenerateSystemDesignReport
from sysbuilder_mcp_server.tools.common import _json, capture_python_output, ensure_sysbuilder_session


@mcp.tool()
def generate_system_design_report(
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    调用 Sysbuilder API `GenerateSystemDesignReport` 生成系统方案设计报告。
    该接口使用固定报告模板，不弹出报告选择窗口。
    """
    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "generate_system_design_report",
                "error": "Failed to start or connect Sysbuilder.",
                "session": session,
            }
        )

    with capture_python_output() as (buf_out, buf_err):
        result = GenerateSystemDesignReport()

    return _json(
        {
            "ok": bool(result),
            "tool": "generate_system_design_report",
            "api": "GenerateSystemDesignReport",
            "report_path": result or "",
            "result": result,
            "session": session,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )

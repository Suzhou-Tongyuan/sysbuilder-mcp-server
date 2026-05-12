"""Sysbuilder session management MCP tools."""
from __future__ import annotations

from typing import Any

from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.path_config import get_sysbuilder_process_path
from sysbuilder_mcp_server.core import ConnectSysbuilder, Exit, FindSysbuilder, StartSysbuilder
from sysbuilder_mcp_server.core.sysbuilder_connect import MwConnect
from sysbuilder_mcp_server.tools.common import _json, capture_python_output


def _serialize_find_result(result: Any) -> dict:
    ports = list(getattr(result, "ports", result or []))
    pids = list(getattr(result, "pids", []))
    return {
        "ports": ports,
        "pids": pids,
        "port_pid_pairs": list(zip(ports, pids)),
    }


@mcp.tool()
def start(
    process_path: str = "",
    ip: str = "",
    port: int = 0,
    args: list[str] | None = None,
) -> str:
    """
    启动 Sysbuilder 并建立连接。

    `process_path` 为空时，会优先尝试使用 `SYSBUILDER_INSTALL_DIR/Bin/Sysbuilder.exe`。
    """
    proc_arg = (process_path or "").strip()
    if not proc_arg:
        default_process = get_sysbuilder_process_path()
        if default_process is not None:
            proc_arg = str(default_process)

    with capture_python_output() as (buf_out, buf_err):
        result = StartSysbuilder(
            processPath=proc_arg or None,
            ip=((ip or "").strip() or None),
            port=(port or None),
            args=args,
        )

    return _json(
        {
            "ok": bool(result),
            "tool": "start",
            "process_path": proc_arg,
            "ip": (ip or "").strip(),
            "port": port or None,
            "args": args or [],
            "result": result,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )


@mcp.tool()
def find() -> str:
    """
    查找当前可连接的 Sysbuilder 实例及端口。
    """
    with capture_python_output() as (buf_out, buf_err):
        result = FindSysbuilder()

    return _json(
        {
            "ok": True,
            "tool": "find",
            "result": _serialize_find_result(result),
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )


@mcp.tool()
def connect(ip: str = "", port: int = 0) -> str:
    """
    连接到已启动的 Sysbuilder。

    `port` 为空时，会先调用 `FindSysbuilder()` 自动选择第一个可用端口。
    """
    with capture_python_output() as (buf_out, buf_err):
        result = ConnectSysbuilder(
            ip=((ip or "").strip() or None),
            port=(port or None),
        )

    return _json(
        {
            "ok": bool(result),
            "tool": "connect",
            "ip": (ip or "").strip(),
            "port": port or None,
            "result": result,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )


@mcp.tool()
def exit() -> str:
    """
    退出当前已连接的 Sysbuilder 软件。

    若当前没有活动连接，则直接返回失败，不会尝试隐式启动或连接。
    """
    conn = MwConnect()
    connected_before = conn.get_is_connected()
    if not connected_before:
        return _json(
            {
                "ok": False,
                "tool": "exit",
                "error": "Sysbuilder is not connected.",
                "connected_before": connected_before,
                "connected_after": connected_before,
            }
        )

    with capture_python_output() as (buf_out, buf_err):
        result = Exit()

    connected_after = MwConnect().get_is_connected()
    return _json(
        {
            "ok": True,
            "tool": "exit",
            "result": result,
            "connected_before": connected_before,
            "connected_after": connected_after,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )

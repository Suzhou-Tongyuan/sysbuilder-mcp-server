"""Sysbuilder session management MCP tools."""
from __future__ import annotations

from typing import Any

from sysbuilder_mcp_server.core import ConnectSysbuilder, Exit, FindSysbuilder, StartSysbuilder
from sysbuilder_mcp_server.core.sysbuilder_connect import MwConnect
from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.path_config import (
    get_sysbuilder_process_path,
    get_sysml_v1_api_host,
    get_sysml_v1_api_port,
    is_sysml_v1_embedded_mode,
)
from sysbuilder_mcp_server.tools.common import _json, capture_python_output


def _serialize_find_result(result: Any) -> dict:
    ports = list(getattr(result, "ports", result or []))
    pids = list(getattr(result, "pids", []))
    return {
        "ports": ports,
        "pids": pids,
        "port_pid_pairs": list(zip(ports, pids)),
    }


def _embedded_endpoint() -> tuple[str, int] | None:
    if not is_sysml_v1_embedded_mode():
        return None
    return get_sysml_v1_api_host(), get_sysml_v1_api_port() or 0


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
    meta={"sysbuilder": {"risk": "write"}},
)
def start(
    process_path: str = "",
    ip: str = "",
    port: int = 0,
    args: list[str] | None = None,
) -> str:
    """
    Launch Sysbuilder and establish the current session directly.

    If `process_path` is empty, the tool will first try
    `SYSBUILDER_INSTALL_DIR/Bin/Sysbuilder.exe`.

    In the default workflow, a successful `start(...)` is sufficient:
    continue modeling directly and do not call `find()` or `connect()` again
    unless the user explicitly asks to connect to an existing instance.
    """
    if _embedded_endpoint() is not None:
        return _json(
            {
                "ok": False,
                "tool": "start",
                "error": "disabled_in_embedded_mode",
                "hint": "The embedded MCP may only use the current SysML v1 process supplied by SYSML_V1_API_HOST/PORT.",
            }
        )

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
            "session_guidance": (
                "start() already launches Sysbuilder and establishes the current session. "
                "After a successful start, continue modeling directly instead of calling find()/connect() again, "
                "unless the user explicitly asks to connect to an existing instance."
            ),
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    meta={"sysbuilder": {"risk": "read"}},
)
def find() -> str:
    """
    Find currently available Sysbuilder instances and ports.

    Use this only when the user explicitly asks to inspect existing instances
    or connect to one that is already running.
    """
    if _embedded_endpoint() is not None:
        return _json(
            {
                "ok": False,
                "tool": "find",
                "error": "disabled_in_embedded_mode",
                "hint": "Instance discovery is forbidden when SYSML_V1_API_PORT identifies the current process.",
            }
        )

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


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    meta={"sysbuilder": {"risk": "read"}},
)
def connect(ip: str = "", port: int = 0) -> str:
    """
    Connect to an already running Sysbuilder instance.

    If `port` is empty, the helper will internally try `FindSysbuilder()` to
    pick the first available port. Prefer this tool only when the user clearly
    wants to attach to an existing instance instead of starting a new one.
    """
    embedded = _embedded_endpoint()
    if embedded is not None:
        ip, port = embedded
        if port == 0:
            return _json(
                {
                    "ok": False,
                    "tool": "connect",
                    "error": "invalid_embedded_port",
                    "hint": "SYSML_V1_API_PORT must be an integer from 1 to 65535; discovery and fallback are disabled.",
                }
            )

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


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": False},
    meta={"sysbuilder": {"risk": "destructive"}},
)
def exit() -> str:
    """
    Exit the currently connected Sysbuilder session.

    If there is no active connection, this returns failure directly and does
    not attempt any implicit launch or reconnect.
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

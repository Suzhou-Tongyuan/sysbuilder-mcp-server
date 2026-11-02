"""Sysbuilder architecture tradeoff MCP tool."""
from __future__ import annotations

from pathlib import Path

from mworks.sysbuilder import RunArchitectureTradeoff
from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.path_config import get_output_root, get_workspace_root
from sysbuilder_mcp_server.tools.common import _json, capture_python_output, ensure_sysbuilder_session


def _resolve_script_path(path: str) -> Path:
    raw = (path or "").strip()
    if not raw:
        raise ValueError("script_path cannot be empty.")
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = (get_workspace_root() / candidate).resolve()
    return candidate


def _resolve_image_dir(path: str) -> str:
    """解析权衡图片目录；未指定时统一写入 MCP 中间数据根目录。"""
    raw = (path or "").strip()
    if raw:
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            candidate = (get_output_root() / candidate).resolve()
    else:
        candidate = get_output_root()
    candidate.mkdir(parents=True, exist_ok=True)
    return str(candidate)


@mcp.tool()
def run_architecture_tradeoff(
    script_path: str,
    image_dir: str = "",
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    调用 Sysbuilder API `RunArchitectureTradeoff` 运行架构权衡脚本并导出图片。

    `script_path` 必须指向已存在的 Python 计算脚本；`image_dir` 为空时写入 MCP 中间数据根目录。
    """
    try:
        resolved_script = _resolve_script_path(script_path)
        resolved_image_dir = _resolve_image_dir(image_dir)
    except ValueError as exc:
        return _json({"ok": False, "tool": "run_architecture_tradeoff", "error": str(exc)})

    if not resolved_script.is_file():
        return _json(
            {
                "ok": False,
                "tool": "run_architecture_tradeoff",
                "error": f"script_path is not a file: {resolved_script}",
            }
        )

    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "run_architecture_tradeoff",
                "error": "Failed to start or connect Sysbuilder.",
                "session": session,
            }
        )

    with capture_python_output() as (buf_out, buf_err):
        result = RunArchitectureTradeoff(
            scriptPath=str(resolved_script),
            imageDir=resolved_image_dir,
        )

    return _json(
        {
            "ok": bool(result),
            "tool": "run_architecture_tradeoff",
            "script_path": str(resolved_script),
            "image_dir": resolved_image_dir,
            "api": "RunArchitectureTradeoff",
            "result": result,
            "session": session,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )

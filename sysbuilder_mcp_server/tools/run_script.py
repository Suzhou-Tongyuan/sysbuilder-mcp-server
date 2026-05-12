"""Run UTF-8 Sysbuilder modeling scripts."""
from __future__ import annotations

from pathlib import Path

from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.path_config import get_workspace_root
from sysbuilder_mcp_server.tools.common import (
    _json,
    ensure_sysbuilder_session,
    ensure_utf8_script_text,
    execute_python_source,
    resolve_output_path,
)


@mcp.tool()
def run_script(
    python_source: str = "",
    script_path: str = "",
    script_name: str = "sysbuilder_modeling_script.py",
    working_directory: str = "",
    auto_save_script: bool = True,
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    执行 Sysbuilder 建模 Python 脚本。

    使用要求：
    - 本工具只负责执行现成的建模脚本。
    - AI 客户端在需要建模时，应先自动生成完整的 Python 建模脚本，再调用本工具执行。
    - 所有执行脚本都会以 UTF-8 保存后再运行。

    入参说明：
    - `python_source`：待执行的完整 Python 建模脚本。
    - `script_path`：已有脚本路径；当 `python_source` 为空时读取这个文件执行。
    - `script_name`：未指定 `script_path` 时，落盘脚本文件名。
    - `working_directory`：脚本执行目录；默认是工作区根目录。
    """
    source = (python_source or "").strip()
    incoming_script_path = (script_path or "").strip()
    if not source and not incoming_script_path:
        return _json(
            {
                "ok": False,
                "tool": "run_script",
                "error": "python_source and script_path cannot both be empty.",
                "hint": "请先由 AI 客户端生成 Python 建模脚本，再通过 python_source 或 script_path 调用本工具。",
            }
        )

    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "run_script",
                "error": "Failed to start or connect Sysbuilder.",
                "session": session,
            }
        )

    saved_path = ""
    if source:
        source = ensure_utf8_script_text(source)
        if auto_save_script or not incoming_script_path:
            target_path = resolve_output_path(incoming_script_path, default_name=script_name)
            target_path.write_text(source, encoding="utf-8")
            saved_path = str(target_path)
        filename = saved_path or "<run_script>"
    else:
        existing_path = Path(incoming_script_path).expanduser()
        if not existing_path.is_absolute():
            existing_path = (get_workspace_root() / existing_path).resolve()
        if not existing_path.is_file():
            return _json(
                {
                    "ok": False,
                    "tool": "run_script",
                    "error": f"script_path is not a file: {existing_path}",
                }
            )
        source = existing_path.read_text(encoding="utf-8")
        saved_path = str(existing_path)
        filename = str(existing_path)

    wd = Path(working_directory).expanduser() if working_directory else get_workspace_root()
    if not wd.is_absolute():
        wd = (get_workspace_root() / wd).resolve()
    wd.mkdir(parents=True, exist_ok=True)

    result = execute_python_source(source=source, filename=filename, working_directory=wd)
    result.update(
        {
            "tool": "run_script",
            "script_path": saved_path,
            "working_directory": str(wd),
            "session": session,
        }
    )
    return _json(result)

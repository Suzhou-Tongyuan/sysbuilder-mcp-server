from __future__ import annotations

import builtins
import io
import json
import os
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from sysbuilder_mcp_server.path_config import (
    get_output_root,
    get_resources_root,
    get_sysbuilder_process_path,
    get_workspace_root,
)
from sysbuilder_mcp_server.core import ConnectSysbuilder, FindSysbuilder, StartSysbuilder
from sysbuilder_mcp_server.core.sysbuilder_connect import MwConnect


_MAX_CAPTURE_CHARS = 400_000


def _json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _truncate(text: str, max_chars: int = _MAX_CAPTURE_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... (truncated, total {len(text)} chars)"


@contextmanager
def capture_python_output() -> Iterator[tuple[io.StringIO, io.StringIO]]:
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = buf_out
    sys.stderr = buf_err
    try:
        yield buf_out, buf_err
    finally:
        sys.stdout = old_out
        sys.stderr = old_err


def resolve_output_path(path: str = "", default_name: str = "") -> Path:
    raw = (path or "").strip()
    if raw:
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            candidate = get_output_root() / candidate
    else:
        candidate = get_output_root() / default_name
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return candidate.resolve()


def ensure_utf8_script_text(source: str) -> str:
    normalized = source.replace("\r\n", "\n")
    lines = normalized.splitlines()
    if not lines:
        return "# -*- coding: utf-8 -*-\n"
    first_two = "\n".join(lines[:2])
    if "coding:" in first_two:
        return normalized
    return "# -*- coding: utf-8 -*-\n" + normalized


def ensure_sysbuilder_session(process_path: str = "", ip: str = "", port: Optional[int] = None) -> Dict[str, Any]:
    conn = MwConnect()
    if conn.get_is_connected():
        return {"ok": True, "action": "already_connected", "stdout": "", "stderr": ""}

    ip_arg = (ip or "").strip() or None
    proc_arg = (process_path or "").strip()
    if not proc_arg:
        default_process = get_sysbuilder_process_path()
        if default_process is not None:
            proc_arg = str(default_process)

    with capture_python_output() as (buf_out, buf_err):
        start_ok = StartSysbuilder(processPath=proc_arg or None, ip=ip_arg, port=port)
    start_stdout = _truncate(buf_out.getvalue())
    start_stderr = _truncate(buf_err.getvalue())
    if start_ok:
        return {
            "ok": True,
            "action": "started",
            "process_path": proc_arg,
            "port": MwConnect().sysbuilderPort,
            "stdout": start_stdout,
            "stderr": start_stderr,
        }

    with capture_python_output() as (buf_out, buf_err):
        ports = FindSysbuilder()
    find_stdout = _truncate(buf_out.getvalue())
    find_stderr = _truncate(buf_err.getvalue())
    available_ports = list(getattr(ports, "ports", ports))
    target_port = port or (available_ports[0] if available_ports else None)
    if target_port is not None:
        with capture_python_output() as (buf_out, buf_err):
            connect_ok = ConnectSysbuilder(ip=ip_arg, port=target_port)
        connect_stdout = _truncate(buf_out.getvalue())
        connect_stderr = _truncate(buf_err.getvalue())
        if connect_ok:
            return {
                "ok": True,
                "action": "connected",
                "process_path": proc_arg,
                "port": target_port,
                "available_ports": available_ports,
                "stdout": "\n".join(filter(None, [start_stdout, find_stdout, connect_stdout])),
                "stderr": "\n".join(filter(None, [start_stderr, find_stderr, connect_stderr])),
            }

    return {
        "ok": False,
        "action": "failed",
        "process_path": proc_arg,
        "port": target_port,
        "available_ports": available_ports,
        "workspace_root": str(get_workspace_root()),
        "resources_root": str(get_resources_root()),
        "output_root": str(get_output_root()),
        "stdout": "\n".join(filter(None, [start_stdout, find_stdout])),
        "stderr": "\n".join(filter(None, [start_stderr, find_stderr])),
    }


def inject_script_namespace(namespace: Dict[str, Any]) -> None:
    namespace["__builtins__"] = builtins
    namespace["WORKSPACE_ROOT"] = str(get_workspace_root())
    namespace["RESOURCES_ROOT"] = str(get_resources_root())
    namespace["OUTPUT_ROOT"] = str(get_output_root())

    import sysbuilder_mcp_server.core as sysbuilder_core

    namespace["sysbuilder"] = sysbuilder_core
    for name in dir(sysbuilder_core):
        if name.startswith("_"):
            continue
        namespace[name] = getattr(sysbuilder_core, name)


@contextmanager
def pushd(target: Path) -> Iterator[None]:
    previous = Path.cwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(previous)


def execute_python_source(source: str, filename: str, working_directory: Path) -> Dict[str, Any]:
    namespace: Dict[str, Any] = {"__name__": "__sysbuilder_mcp_run_script__"}
    inject_script_namespace(namespace)

    buf_out = io.StringIO()
    buf_err = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout = buf_out
        sys.stderr = buf_err
        with pushd(working_directory):
            exec(compile(source, filename, "exec"), namespace, namespace)
    except Exception as exc:
        return {
            "ok": False,
            "stdout": _truncate(buf_out.getvalue()),
            "stderr": _truncate(buf_err.getvalue()),
            "exception": str(exc),
            "traceback": _truncate(traceback.format_exc()),
            "run_script_result": namespace.get("RUN_SCRIPT_RESULT"),
        }
    finally:
        sys.stdout = old_out
        sys.stderr = old_err

    return {
        "ok": True,
        "stdout": _truncate(buf_out.getvalue()),
        "stderr": _truncate(buf_err.getvalue()),
        "exception": "",
        "traceback": "",
        "run_script_result": namespace.get("RUN_SCRIPT_RESULT"),
    }

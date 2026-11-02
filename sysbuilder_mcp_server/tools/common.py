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
    get_sysml_v1_api_host,
    get_sysml_v1_api_port,
    get_workspace_root,
    is_sysml_v1_embedded_mode,
)
from sysbuilder_mcp_server.core import ConnectSysbuilder, StartSysbuilder
from sysbuilder_mcp_server.core.resources_manifest import (
    load_runtime_resource_bundle,
    load_runtime_resource_texts,
)
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
    embedded_host = get_sysml_v1_api_host()
    embedded_port = get_sysml_v1_api_port()
    if is_sysml_v1_embedded_mode():
        if embedded_port is None:
            return {
                "ok": False,
                "action": "embedded_connection_failed",
                "error": "SYSML_V1_API_PORT must be an integer from 1 to 65535.",
                "stdout": "",
                "stderr": "",
            }
        if conn.get_is_connected() and int(getattr(conn, "sysbuilderPort", 0) or 0) == embedded_port:
            return {
                "ok": True,
                "action": "already_connected_embedded",
                "ip": embedded_host or "127.0.0.1",
                "port": embedded_port,
                "stdout": "",
                "stderr": "",
            }
        with capture_python_output() as (buf_out, buf_err):
            connected = ConnectSysbuilder(ip=embedded_host or None, port=embedded_port)
        return {
            "ok": bool(connected),
            "action": "connected_embedded" if connected else "embedded_connection_failed",
            "ip": embedded_host or "127.0.0.1",
            "port": embedded_port,
            "stdout": _truncate(buf_out.getvalue()),
            "stderr": _truncate(buf_err.getvalue()),
            "hint": "The embedded AI is pinned to the current SysBuilder process and will not start or select another instance.",
        }

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

    return {
        "ok": False,
        "action": "failed",
        "process_path": proc_arg,
        "port": port,
        "workspace_root": str(get_workspace_root()),
        "resources_root": str(get_resources_root()),
        "output_root": str(get_output_root()),
        "stdout": start_stdout,
        "stderr": start_stderr,
        "hint": "Default MCP behavior is to start a new Sysbuilder session. If you explicitly want to connect to an existing instance, use the dedicated session connection tools instead of run_script auto-session.",
    }


def inject_script_namespace(namespace: Dict[str, Any]) -> None:
    resource_bundle = load_runtime_resource_bundle()

    def get_modeling_rule_text(name: str = "") -> str:
        key = (name or "sysbuilder_rules").strip()
        entry = resource_bundle.get(key)
        return str(entry.get("text", "")) if isinstance(entry, dict) else ""

    def get_modeling_rule_bundle() -> Dict[str, Dict[str, Any]]:
        return resource_bundle

    def print_modeling_rule_summary() -> str:
        ordered_keys = (
            "sysbuilder_rules",
            "sysbuilder_python_api",
            "sysml_skill",
            "sysml_reference",
            "default_rules",
        )
        sections = []
        for key in ordered_keys:
            entry = resource_bundle.get(key)
            if not isinstance(entry, dict) or not entry.get("ok"):
                continue
            summary = str(entry.get("summary", "")).strip()
            if not summary:
                continue
            sections.append(f"[{key}] {entry.get('path')}\n{summary}")
        text = "\n\n".join(sections)
        if text:
            print(text)
        return text

    namespace["__builtins__"] = builtins
    namespace["WORKSPACE_ROOT"] = str(get_workspace_root())
    namespace["RESOURCES_ROOT"] = str(get_resources_root())
    namespace["OUTPUT_ROOT"] = str(get_output_root())
    namespace["RESOURCE_TEXTS"] = load_runtime_resource_texts()
    namespace["RESOURCE_BUNDLE"] = resource_bundle
    namespace["MODELING_RULES"] = resource_bundle
    namespace["SYSBUILDER_MODELING_RULES_TEXT"] = get_modeling_rule_text("sysbuilder_rules")
    namespace["SYSBUILDER_PYTHON_API_TEXT"] = get_modeling_rule_text("sysbuilder_python_api")
    namespace["SYSML_MODELING_SKILL_TEXT"] = get_modeling_rule_text("sysml_skill")
    namespace["SYSML_MODELING_REFERENCE_TEXT"] = get_modeling_rule_text("sysml_reference")
    namespace["GetModelingRuleText"] = get_modeling_rule_text
    namespace["GetModelingRuleBundle"] = get_modeling_rule_bundle
    namespace["PrintModelingRuleSummary"] = print_modeling_rule_summary

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


def get_runtime_modeling_rules_metadata() -> Dict[str, Any]:
    bundle = load_runtime_resource_bundle()
    return {
        "auto_loaded": True,
        "available_globals": [
            "OUTPUT_ROOT",
            "MODELING_RULES",
            "RESOURCE_BUNDLE",
            "SYSBUILDER_MODELING_RULES_TEXT",
            "SYSBUILDER_PYTHON_API_TEXT",
            "SYSML_MODELING_SKILL_TEXT",
            "SYSML_MODELING_REFERENCE_TEXT",
            "GetModelingRuleText",
            "GetModelingRuleBundle",
            "PrintModelingRuleSummary",
        ],
        "resources": {
            key: {
                "path": value.get("path", ""),
                "ok": bool(value.get("ok")),
                "summary": value.get("summary", ""),
            }
            for key, value in bundle.items()
        },
    }

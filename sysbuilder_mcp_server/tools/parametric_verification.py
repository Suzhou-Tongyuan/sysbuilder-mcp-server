"""关系映射与参数图计算 MCP 工具。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mworks.sysbuilder import CalculateParametricDiagram, CreateRelationMapping
from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.tools.common import (
    _json,
    capture_python_output,
    ensure_sysbuilder_session,
)


def _read_calculation_result(result_path: str) -> tuple[Any, str]:
    """读取参数图计算结果，适用于 MCP 直接返回 values/error 的场景。"""
    if not result_path:
        return None, "CalculateParametricDiagram returned an empty result path."

    path = Path(result_path)
    if not path.is_file():
        return None, f"Parameter calculation result file does not exist: {path}"

    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), ""
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        # 后端已完成调用但结果文件不可读时，保留原始路径并返回明确诊断。
        return None, f"Failed to read parameter calculation result: {exc}"


@mcp.tool()
def create_relation_mapping(
    source_full_name: str,
    target_full_name: str,
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    创建源变量到目标变量的关系映射。

    适用于需求指标、活动输入/输出接口、块值属性和约束输入/输出参数等可映射变量。
    建立映射前应先创建两端元素，并保证数据类型、单位和值语义兼容。
    """
    source = (source_full_name or "").strip()
    target = (target_full_name or "").strip()
    if not source or not target:
        return _json(
            {
                "ok": False,
                "tool": "create_relation_mapping",
                "error": "source_full_name and target_full_name cannot be empty.",
            }
        )
    if source == target:
        return _json(
            {
                "ok": False,
                "tool": "create_relation_mapping",
                "error": "source_full_name and target_full_name cannot refer to the same variable.",
                "source_full_name": source,
                "target_full_name": target,
            }
        )

    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "create_relation_mapping",
                "error": "Failed to start or connect Sysbuilder.",
                "session": session,
            }
        )

    with capture_python_output() as (buf_out, buf_err):
        result = CreateRelationMapping(
            sourceFullName=source,
            targetFullName=target,
        )

    return _json(
        {
            "ok": bool(result),
            "tool": "create_relation_mapping",
            "api": "CreateRelationMapping",
            "source_full_name": source,
            "target_full_name": target,
            "direction": "source_to_target",
            "result": result,
            "session": session,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )


@mcp.tool()
def calculate_parametric_diagram(
    full_name: str,
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    计算指定参数图，并读取 parameter_calculation.json 中的数值或错误信息。

    该工具不会打开参数图或切换当前视图。调用前应完成约束表达式、参数图绑定和关系映射。
    """
    diagram_full_name = (full_name or "").strip()
    if not diagram_full_name:
        return _json(
            {
                "ok": False,
                "tool": "calculate_parametric_diagram",
                "error": "full_name cannot be empty.",
            }
        )

    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "calculate_parametric_diagram",
                "error": "Failed to start or connect Sysbuilder.",
                "session": session,
            }
        )

    with capture_python_output() as (buf_out, buf_err):
        result_path = CalculateParametricDiagram(fullName=diagram_full_name)

    calculation_result, read_error = _read_calculation_result(result_path)
    calculation_error = ""
    if isinstance(calculation_result, dict):
        calculation_error = str(calculation_result.get("error") or "").strip()

    return _json(
        {
            "ok": bool(result_path) and not read_error and not calculation_error,
            "tool": "calculate_parametric_diagram",
            "api": "CalculateParametricDiagram",
            "full_name": diagram_full_name,
            "result_path": result_path,
            "calculation_result": calculation_result,
            "error": calculation_error or read_error,
            "session": session,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )

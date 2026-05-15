"""High-level traceability helpers for Sysbuilder models."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sysbuilder_mcp_server.core import (
    AutoLayoutDiagram,
    CreateAllocateLine,
    CreateRequirementSatisfyLine,
    InsertElementToDiagram,
)
from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.tools.common import (
    _json,
    _truncate,
    capture_python_output,
    ensure_sysbuilder_session,
)


def _call_api(func, *args, **kwargs) -> Dict[str, Any]:
    with capture_python_output() as (buf_out, buf_err):
        value = func(*args, **kwargs)
    return {
        "ok": bool(value),
        "return_value": value,
        "stdout": _truncate(buf_out.getvalue()),
        "stderr": _truncate(buf_err.getvalue()),
    }


def _as_position(value: Optional[List[int]]) -> Optional[List[int]]:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("position must be a two-item list, for example [120, 240].")
    return value


@mcp.tool()
def create_satisfy_trace(
    diagram_full_name: str,
    satisfier_full_name: str,
    requirement_full_name: str,
    satisfier_position: Optional[List[int]] = None,
    requirement_position: Optional[List[int]] = None,
    auto_layout: bool = True,
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    创建 satisfy 追溯关系，并自动把两端元素插入目标需求图。

    适用场景：
    - 当脚本或模型中存在需求与实现元素时，应优先调用本工具建立追溯。
    - satisfy 方向固定为：满足方/实现方 -> 需求。
    - `diagram_full_name` 推荐传需求图（REQ Diagram）。

    本工具内部执行：
    1. `InsertElementToDiagram(satisfier_full_name, diagram_full_name, ...)`
    2. `InsertElementToDiagram(requirement_full_name, diagram_full_name, ...)`
    3. `CreateRequirementSatisfyLine(diagram_full_name, satisfier_full_name, requirement_full_name)`
    4. 可选 `AutoLayoutDiagram(diagram_full_name)`
    """
    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json({"ok": False, "tool": "create_satisfy_trace", "error": "Failed to start or connect Sysbuilder.", "session": session})

    try:
        start_position = _as_position(satisfier_position)
        end_position = _as_position(requirement_position)
    except ValueError as exc:
        return _json({"ok": False, "tool": "create_satisfy_trace", "error": str(exc), "session": session})

    operations = {
        "insert_satisfier": _call_api(InsertElementToDiagram, satisfier_full_name, diagram_full_name, start_position),
        "insert_requirement": _call_api(InsertElementToDiagram, requirement_full_name, diagram_full_name, end_position),
        "create_satisfy": _call_api(
            CreateRequirementSatisfyLine,
            diagram_full_name,
            satisfier_full_name,
            requirement_full_name,
        ),
    }
    if auto_layout:
        operations["auto_layout"] = _call_api(AutoLayoutDiagram, diagram_full_name)

    ok = bool(operations["create_satisfy"]["ok"])
    warnings = []
    for key in ("insert_satisfier", "insert_requirement"):
        if not operations[key]["ok"]:
            warnings.append(f"{key} returned false; the element may already be in the diagram or insertion may need GUI verification.")

    return _json(
        {
            "ok": ok,
            "tool": "create_satisfy_trace",
            "diagram_full_name": diagram_full_name,
            "satisfier_full_name": satisfier_full_name,
            "requirement_full_name": requirement_full_name,
            "direction": "satisfier -> requirement",
            "operations": operations,
            "warnings": warnings,
            "session": session,
        }
    )


@mcp.tool()
def create_allocate_trace(
    diagram_full_name: str,
    source_full_name: str,
    target_full_name: str,
    source_position: Optional[List[int]] = None,
    target_position: Optional[List[int]] = None,
    auto_layout: bool = True,
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    创建 allocate 追溯关系，并自动把两端元素插入目标模块定义图。

    适用场景：
    - 当模型中存在功能/活动与结构块时，应优先调用本工具建立分配关系。
    - allocate 推荐方向为：功能或活动 -> 结构块。
    - `diagram_full_name` 推荐传模块定义图（BDD）。

    本工具内部执行：
    1. `InsertElementToDiagram(source_full_name, diagram_full_name, ...)`
    2. `InsertElementToDiagram(target_full_name, diagram_full_name, ...)`
    3. `CreateAllocateLine(diagram_full_name, source_full_name, target_full_name)`
    4. 可选 `AutoLayoutDiagram(diagram_full_name)`
    """
    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json({"ok": False, "tool": "create_allocate_trace", "error": "Failed to start or connect Sysbuilder.", "session": session})

    try:
        start_position = _as_position(source_position)
        end_position = _as_position(target_position)
    except ValueError as exc:
        return _json({"ok": False, "tool": "create_allocate_trace", "error": str(exc), "session": session})

    operations = {
        "insert_source": _call_api(InsertElementToDiagram, source_full_name, diagram_full_name, start_position),
        "insert_target": _call_api(InsertElementToDiagram, target_full_name, diagram_full_name, end_position),
        "create_allocate": _call_api(
            CreateAllocateLine,
            diagram_full_name,
            source_full_name,
            target_full_name,
        ),
    }
    if auto_layout:
        operations["auto_layout"] = _call_api(AutoLayoutDiagram, diagram_full_name)

    ok = bool(operations["create_allocate"]["ok"])
    warnings = []
    for key in ("insert_source", "insert_target"):
        if not operations[key]["ok"]:
            warnings.append(f"{key} returned false; the element may already be in the diagram or insertion may need GUI verification.")

    return _json(
        {
            "ok": ok,
            "tool": "create_allocate_trace",
            "diagram_full_name": diagram_full_name,
            "source_full_name": source_full_name,
            "target_full_name": target_full_name,
            "direction": "function_or_activity -> structure_block",
            "operations": operations,
            "warnings": warnings,
            "session": session,
        }
    )

"""IBD 内部属性显示工具，复用 Sysbuilder 组成属性视图接口。"""
from __future__ import annotations

from sysbuilder_mcp_server.core import ShowInternalProperties
from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.tools.common import _json, capture_python_output, ensure_sysbuilder_session


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False,
                 "idempotentHint": True, "openWorldHint": False},
    meta={"sysbuilder": {"risk": "write"}},
)
def show_internal_properties(
    full_diagram_name: str,
    parent_property_path: str,
    property_names: list[str] | None = None,
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """在 IBD 的已有组成属性中显示其类型的子属性，可按路径逐层展开。

    先 NewPartProperty、SetType、InsertElementToDiagram，再调用本工具。
    parent_property_path 使用 partA 或 partA.child 等视图路径；含点名称用单引号。
    property_names 省略显示全部非接口子属性，列表增量显示指定子属性，[] 不新增。
    保留已有图元和连线，重复调用不重复创建。通过 run_script 中的
    CreateConnectorLine / CreateBindingConnectorLine 连接 partA.child.port 等端点。
    显示全部图元并完成连线后调用现有 AutoLayoutDiagram 统一布局。
    """
    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json({"ok": False, "tool": "show_internal_properties", "session": session,
                      "error": "Failed to start or connect Sysbuilder."})
    with capture_python_output() as (stdout, stderr):
        result = ShowInternalProperties(
            fullDiagramName=full_diagram_name,
            parentPropertyPath=parent_property_path,
            propertyNames=property_names,
        )
    return _json({
        "ok": bool(result), "tool": "show_internal_properties",
        "api": "ShowInternalProperties", "result": result, "session": session,
        "full_diagram_name": full_diagram_name, "parent_property_path": parent_property_path,
        "property_names": property_names,
        "stdout": stdout.getvalue(), "stderr": stderr.getvalue(),
    })

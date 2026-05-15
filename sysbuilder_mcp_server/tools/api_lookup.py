"""Sysbuilder API lookup MCP tool."""
from __future__ import annotations

from sysbuilder_mcp_server.core.api_catalog import (
    API_FILE_PATH,
    get_api_entry,
    list_api_entries,
    search_api_entries,
    suggest_api_entries,
)
from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.tools.common import _json


_STATE_MACHINE_RELATED_APIS = (
    "NewStateMachine",
    "NewSTMDiagram",
    "CreateState",
    "CreateCompositeState",
    "CreateOrthogonalState",
    "CreateStateInitialNode",
    "CreateStateChoiceNode",
    "CreateStateForkNode",
    "CreateStateJoinNode",
    "CreateStateFinalNode",
    "CreateStateTerminateNode",
    "CreateStateTransitionLineByGraphName",
    "NewValueProperty",
    "SetType",
    "SetDefaultValue",
    "NewOpaqueBehavior",
    "SetOpaqueBehaviorScript",
    "SetStateEntry",
    "SetStateDoActivity",
    "SetStateExit",
)

_ACTIVITY_RELATED_APIS = (
    "NewACTDiagram",
    "NewActivity",
    "NewInputPort",
    "NewOutputPort",
    "SetActivityScript",
    "CreateActivityDecisionNode",
    "CreateActivityMergeNode",
    "CreateActivityForkNode",
    "CreateActivityJoinNode",
    "CreateActivityControlFlowLine",
    "CreateActivityControlFlowLineByGraphName",
    "CreateActivityObjectFlowLine",
    "CreateActivityObjectFlowLineByGraphName",
    "CreateActivityEventNode",
    "CreateActivitySignalNode",
    "CreateActivityTimeEventNode",
)

_STATE_MACHINE_QUERY_TOKENS = (
    "state",
    "stm",
    "statemachine",
    "transition",
    "doactivity",
    "entry",
    "exit",
    "opaquebehavior",
    "valueproperty",
    "状态",
    "状态机",
    "迁移",
    "不透明行为",
    "值属性",
)

_ACTIVITY_QUERY_TOKENS = (
    "activity",
    "actdiagram",
    "controlflow",
    "objectflow",
    "decision",
    "活动",
    "活动图",
    "控制流",
    "对象流",
    "选择",
    "决策",
    "信号",
    "事件",
    "时间事件",
)


def _collect_api_entries(names: tuple[str, ...]) -> list[dict[str, object]]:
    collected: list[dict[str, object]] = []
    seen: set[str] = set()
    for name in names:
        entry = get_api_entry(name)
        if not entry:
            continue
        entry_name = str(entry.get("name", ""))
        if not entry_name or entry_name in seen:
            continue
        seen.add(entry_name)
        collected.append(entry)
    return collected


def _is_state_machine_lookup(query: str, api_name: str, matches: list[dict[str, object]]) -> bool:
    raw = f"{query} {api_name}".lower()
    if any(token in raw for token in _STATE_MACHINE_QUERY_TOKENS):
        return True

    state_prefixes = ("NewState", "CreateState", "SetState")
    state_exact = {"NewSTMDiagram", "NewOpaqueBehavior", "NewValueProperty", "SetOpaqueBehaviorScript"}
    for item in matches:
        name = str(item.get("name", ""))
        if name.startswith(state_prefixes) or name in state_exact:
            return True
    return False


def _is_activity_lookup(query: str, api_name: str, matches: list[dict[str, object]]) -> bool:
    raw = f"{query} {api_name}".lower()
    if any(token in raw for token in _ACTIVITY_QUERY_TOKENS):
        return True

    activity_prefixes = ("NewACT", "CreateActivity", "SetActivity")
    activity_exact = {"NewActivity", "NewInputPort", "NewOutputPort"}
    for item in matches:
        name = str(item.get("name", ""))
        if name.startswith(activity_prefixes) or name in activity_exact:
            return True
    return False


def _build_state_machine_guidance() -> dict[str, object]:
    return {
        "related_apis": _collect_api_entries(_STATE_MACHINE_RELATED_APIS),
        "usage_patterns": [
            "状态机变量通常需要一起查询 NewValueProperty、SetType、SetDefaultValue；迁移条件里用到的变量必须先在该状态机下创建同名值属性。",
            "CreateStateTransitionLineByGraphName / CreateStateTransitionLine 的 lineName 如果写了迁移条件，则条件中的变量必须先在该状态机下创建同名值属性，并先设置类型与默认值。",
            "状态迁移条件中的逻辑与、逻辑或、逻辑非统一使用 `&&`、`||`、`!`；不要使用 `and`、`or`、`not`。",
            "状态动作通常需要一起查询 NewOpaqueBehavior、SetOpaqueBehaviorScript、SetStateEntry、SetStateDoActivity、SetStateExit。",
            "SetStateEntry/SetStateDoActivity/SetStateExit 的 fullName 必须是目标状态元素的完整元素名，写法为“状态机全名 + '.' + 状态名”；不要传图名、graphName 或猜测别名。",
            "SetStateEntry/SetStateDoActivity/SetStateExit 的 behaviorFullName 可以直接传不透明行为 OpaqueBehavior 的完整元素名，不必局限于 Activity。",
            "推荐顺序：先 NewStateMachine / NewSTMDiagram / CreateState*，再补 NewValueProperty + SetType + SetDefaultValue，最后 NewOpaqueBehavior + SetOpaqueBehaviorScript + SetStateDoActivity。",
        ],
        "recommended_snippets": [
            {
                "topic": "state_value_property",
                "snippet": (
                    'NewValueProperty("AutoDoorV3.Behavior.DoorStateMachine.timeout_counter")\n'
                    'SetType("AutoDoorV3.Behavior.DoorStateMachine.timeout_counter", "Integer")\n'
                    'SetDefaultValue("AutoDoorV3.Behavior.DoorStateMachine.timeout_counter", "0")'
                ),
            },
            {
                "topic": "state_opaque_behavior",
                "snippet": (
                    'NewOpaqueBehavior("AutoDoorV3.Behavior.DoorStateMachine.CloseDoorAction")\n'
                    'SetOpaqueBehaviorScript("AutoDoorV3.Behavior.DoorStateMachine.CloseDoorAction", "timeout_counter = 0", "Groovy")\n'
                    'SetStateDoActivity("AutoDoorV3.Behavior.DoorStateMachine.Closed", '
                    '"AutoDoorV3.Behavior.DoorStateMachine.CloseDoorAction")'
                ),
            },
            {
                "topic": "state_full_name_rule",
                "snippet": (
                    '# 状态全名 = 状态机全名 + "." + 状态名\n'
                    'stm = "AutoDoorV3.Behavior.DoorStateMachine"\n'
                    'state_full_name = f"{stm}.Closed"'
                ),
            },
        ],
    }


def _build_activity_guidance() -> dict[str, object]:
    return {
        "related_apis": _collect_api_entries(_ACTIVITY_RELATED_APIS),
        "usage_patterns": [
            "活动图中前置活动到选择节点的唯一输入线必须优先使用对象流；前置活动应先通过脚本给输出端口赋值。",
            "每个普通活动默认只允许 1 条输入线；若存在多路汇聚需求，应改用合并节点或汇合节点，不要把多条 incoming 线直接接到同一个活动。",
            "选择节点出线上的 guard 不允许只写 `[允许启动]`、`[检测到故障]` 这类结论标签；guard 必须显式引用传入该选择节点的对象流端口名，并写成可判断的布尔表达式，例如 `[start_result == true]`、`[fault_flag == true]`。",
            "活动图 guard 中的逻辑与、逻辑或、逻辑非统一使用 `&&`、`||`、`!`；不要使用 `and`、`or`、`not`，例如 `[target_valid == true && fault_flag == false]`。",
            "真正的活动接口默认只用 NewInputPort 和 NewOutputPort；不要额外创建无连接接口。",
            "非必要不要使用 CreateActivityEventNode、CreateActivitySignalNode、CreateActivityTimeEventNode；只有在确有外部事件、信号收发或定时/延时语义时才使用。",
        ],
        "avoid_apis_unless_explicitly_needed": _collect_api_entries(
            (
                "CreateActivityEventNode",
                "CreateActivitySignalNode",
                "CreateActivityTimeEventNode",
            )
        ),
    }


@mcp.tool()
def lookup_sysbuilder_api(
    query: str = "",
    api_name: str = "",
    limit: int = 20,
) -> str:
    """
    Query the MCP-bundled Sysbuilder Python API catalog.

    Suggested usage:
    - If you know the exact API name, pass `api_name`
    - If you only know keywords or intent, pass `query`
    - If both are empty, the first `limit` APIs are returned
    """
    capped_limit = min(max(limit or 20, 1), 200)
    exact = get_api_entry(api_name) if (api_name or "").strip() else None
    matches = [exact] if exact else search_api_entries(query=query, limit=capped_limit)
    fallback_used = False
    if not matches:
        matches = suggest_api_entries(query=(api_name or query), limit=capped_limit)
        fallback_used = True

    semantic_guidance: dict[str, object] = {
        "general_modeling_cautions": [
            "非必要不要使用时间、信号和时间事件相关节点；只有在需求明确要求定时/延时、信号收发或外部事件触发时才使用。",
        ]
    }
    if _is_state_machine_lookup(query=query, api_name=api_name, matches=matches):
        semantic_guidance["state_machine"] = _build_state_machine_guidance()
    if _is_activity_lookup(query=query, api_name=api_name, matches=matches):
        semantic_guidance["activity"] = _build_activity_guidance()

    return _json(
        {
            "ok": True,
            "tool": "lookup_sysbuilder_api",
            "api_source": str(API_FILE_PATH),
            "query": (query or "").strip(),
            "api_name": (api_name or "").strip(),
            "limit": capped_limit,
            "match_count": len(matches),
            "fallback_used": fallback_used,
            "search_mode": "exact_or_partial_then_fallback",
            "matches": matches,
            "semantic_guidance": semantic_guidance,
            "hint": (
                "No exact/partial match was found, so fallback suggestions are returned."
                if fallback_used
                else "Matched by exact name or partial keyword."
            ),
            "recommended_workflow": [
                "First use lookup_sysbuilder_api to confirm the API names and signatures you need.",
                "Then write one complete script and execute it with run_script.",
                "If an API is not found, rewrite the approach using exposed APIs instead of guessing similar names.",
            ],
            "catalog_size": len(list_api_entries()),
        }
    )

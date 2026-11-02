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
    "CreateSubState",
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

_DODAF_UAF_RELATED_APIS = (
    "NewAV1Diagram", "NewAV2Diagram", "NewAV3Diagram",
    "NewCV1aDiagram", "NewCV1bDiagram", "NewCV2Diagram", "NewCV3Diagram", "NewCV4Diagram", "NewCV5Diagram",
    "NewOV1aDiagram", "NewOV1bDiagram", "NewOV1cDiagram", "NewOV1dDiagram", "NewOV1fDiagram", "NewOV2Diagram", "NewOV4Diagram", "NewOV5aDiagram", "NewOV5bDiagram", "NewOV6bDiagram", "NewOV6cDiagram",
    "NewSV1aDiagram", "NewSV1bDiagram", "NewSV2Diagram", "NewSV3Diagram", "NewSV4Diagram", "NewSV4bDiagram", "NewSV5aDiagram", "NewSV5bDiagram", "NewSV5cDiagram",
    "NewDIV1Diagram",
)

_SEMANTIC_EXPORT_RELATED_APIS = ("ExportSemanticJson",)
_ARCHITECTURE_TRADEOFF_RELATED_APIS = ("RunArchitectureTradeoff",)
_INSTANCE_RELATED_APIS = ("NewInstance", "SetType", "SetDefaultValue", "SetUnit")
_IBD_RELATED_APIS = (
    "NewIBDDiagram", "NewPartProperty", "SetType", "InsertElementToDiagram",
    "ShowInternalProperties", "CreateConnectorLine", "CreateBindingConnectorLine", "CreateItemFlow",
)
_DIAGRAM_LAYOUT_RELATED_APIS = (
    "InsertElementToDiagram",
    "AutoLayoutDiagram",
    "AdjustDiagramFrameToOptimalSize",
    "ExportDiagramImage",
)

_RELATION_MAPPING_RELATED_APIS = (
    "CreateRelationMapping",
    "CalculateParametricDiagram",
    "NewRequirementIndex",
    "NewInputPort",
    "NewOutputPort",
    "NewValueProperty",
    "NewConstraintBlock",
    "NewConstraintProperty",
    "NewPARDiagram",
    "NewInputParam",
    "NewOutputParam",
    "NewReturnParam",
    "SetType",
    "SetUnit",
    "SetDefaultValue",
    "SetConstraintExpression",
    "CreateBindingConnectorLine",
)
_TEAM_RELATED_APIS = (
    "LoginTeam",
    "LogoutTeam",
    "GetTeamSessionInfo",
    "ListTeamResources",
    "SearchPublicTeamRepositories",
    "ListLocalTeamRepositories",
    "CreateTeamGroup",
    "UpdateTeamGroup",
    "DeleteTeamGroup",
    "CreateTeamRepository",
    "CloneTeamRepository",
    "CloneTeamGroup",
    "PublishProjectToTeam",
    "GetTeamRepositoryStatus",
    "CommitTeamRepository",
    "PullTeamRepository",
    "PushTeamRepository",
    "GetTeamRepositoryHistory",
    "GetTeamCommitDetails",
    "RestoreTeamRepositoryFiles",
    "ResetTeamRepositoryVersion",
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

_DODAF_UAF_QUERY_TOKENS = (
    "dodaf", "uaf", "av", "cv", "ov", "sv", "div",
    "体系视图", "作战视图", "能力视图", "系统视图",
)

_SEMANTIC_EXPORT_QUERY_TOKENS = ("semantic", "json", "语义", "语义树", "语义json")
_ARCHITECTURE_TRADEOFF_QUERY_TOKENS = ("tradeoff", "trade-off", "架构权衡", "权衡分析")
_INSTANCE_QUERY_TOKENS = ("instance", "usage", "实例", "值实例")
_DIAGRAM_LAYOUT_QUERY_TOKENS = (
    "autolayout",
    "adjustdiagramframe",
    "layout",
    "frame",
    "canvas",
    "自动布局",
    "画布",
    "边框",
    "最佳尺寸",
)
_RELATION_MAPPING_QUERY_TOKENS = (
    "createrelationmapping",
    "calculateparametricdiagram",
    "relation mapping",
    "parametric calculation",
    "constraint calculation",
    "requirement verification",
    "关系映射",
    "需求指标映射",
    "活动接口映射",
    "块值属性映射",
    "约束参数映射",
    "参数图计算",
    "约束计算",
    "验证需求指标",
)
_TEAM_QUERY_TOKENS = (
    "team",
    "collaboration",
    "collaborative",
    "repository",
    "团队",
    "协同",
    "协作",
    "团队资源",
    "团队仓库",
    "公共仓库",
    "本地仓库",
    "提交历史",
    "拉取",
    "推送",
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
    state_exact = {"NewSTMDiagram", "NewOpaqueBehavior", "NewValueProperty", "SetOpaqueBehaviorScript", "CreateSubState"}
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


def _is_dodaf_uaf_lookup(query: str, api_name: str, matches: list[dict[str, object]]) -> bool:
    raw = f"{query} {api_name}".lower()
    if any(token.lower() in raw for token in _DODAF_UAF_QUERY_TOKENS):
        return True
    return any(str(item.get("name", "")).startswith(("NewAV", "NewCV", "NewOV", "NewSV", "NewDIV")) for item in matches)


def _is_semantic_export_lookup(query: str, api_name: str, matches: list[dict[str, object]]) -> bool:
    raw = f"{query} {api_name}".lower()
    if any(token.lower() in raw for token in _SEMANTIC_EXPORT_QUERY_TOKENS):
        return True
    return any(str(item.get("name", "")) == "ExportSemanticJson" for item in matches)


def _is_architecture_tradeoff_lookup(query: str, api_name: str, matches: list[dict[str, object]]) -> bool:
    raw = f"{query} {api_name}".lower()
    if any(token.lower() in raw for token in _ARCHITECTURE_TRADEOFF_QUERY_TOKENS):
        return True
    return any(str(item.get("name", "")) == "RunArchitectureTradeoff" for item in matches)


def _is_instance_lookup(query: str, api_name: str, matches: list[dict[str, object]]) -> bool:
    raw = f"{query} {api_name}".lower()
    if any(token.lower() in raw for token in _INSTANCE_QUERY_TOKENS):
        return True
    return any(str(item.get("name", "")) == "NewInstance" for item in matches)


def _is_diagram_layout_lookup(query: str, api_name: str, matches: list[dict[str, object]]) -> bool:
    """判断本次查询是否需要返回视图布局与画布边框操作指引。"""
    raw = f"{query} {api_name}".lower()
    if any(token.lower() in raw for token in _DIAGRAM_LAYOUT_QUERY_TOKENS):
        return True
    related_names = set(_DIAGRAM_LAYOUT_RELATED_APIS)
    return any(str(item.get("name", "")) in related_names for item in matches)


def _is_relation_mapping_lookup(query: str, api_name: str, matches: list[dict[str, object]]) -> bool:
    """判断本次查询是否需要返回关系映射与参数图计算指引。"""
    raw = f"{query} {api_name}".lower()
    if any(token.lower() in raw for token in _RELATION_MAPPING_QUERY_TOKENS):
        return True
    related_names = {"CreateRelationMapping", "CalculateParametricDiagram"}
    return any(str(item.get("name", "")) in related_names for item in matches)


def _is_team_collaboration_lookup(
    query: str,
    api_name: str,
    matches: list[dict[str, object]],
) -> bool:
    """判断本次查询是否需要返回团队协同操作指引。"""
    raw = f"{query} {api_name}".lower()
    if any(token.lower() in raw for token in _TEAM_QUERY_TOKENS):
        return True
    return any(str(item.get("name", "")) in _TEAM_RELATED_APIS for item in matches)


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


def _build_dodaf_uaf_guidance() -> dict[str, object]:
    return {
        "related_apis": _collect_api_entries(_DODAF_UAF_RELATED_APIS),
        "usage_patterns": [
            "创建 DoDAF/UAF 视图前必须用 NewProject(..., projectType='dodaf') 新建 DoDAF 工程，否则固定父包 AV/CV/OV/SV/DIV 不存在时会创建失败。",
            "这些视图 API 只传 diagramName，软件会自动拼接固定父包路径，例如 AV.'AV-1'.图名；不要传完整路径。",
        ],
    }

def _build_semantic_export_guidance() -> dict[str, object]:
    return {
        "related_apis": _collect_api_entries(_SEMANTIC_EXPORT_RELATED_APIS),
        "usage_patterns": [
            "ExportSemanticJson(...) 返回导出的 JSON 文件路径，不直接返回 JSON 内容。",
            "path 为空时由 Sysbuilder 使用默认 semantic_tree.json；fullName 为空导出全工程，非空导出指定元素子树。",
        ],
    }

def _build_architecture_tradeoff_guidance() -> dict[str, object]:
    return {
        "related_apis": _collect_api_entries(_ARCHITECTURE_TRADEOFF_RELATED_APIS),
        "usage_patterns": [
            "RunArchitectureTradeoff(scriptPath, imageDir) 需要传入已存在、可读取的 Python 计算脚本路径。",
            "imageDir 为空时由 Sysbuilder 在工程工作路径下自动创建输出目录；返回值为实际图片输出目录。",
        ],
    }

def _build_instance_guidance() -> dict[str, object]:
    return {
        "related_apis": _collect_api_entries(_INSTANCE_RELATED_APIS),
        "usage_patterns": [
            "NewInstance(fullName, definitionFullName) 会按定义创建实例；definitionFullName 可以是模型定义全名，也可以是 Real/Integer/Boolean/String 等基础值类型短名。",
            "需要默认值、单位或类型约束时，创建实例后再配合 SetDefaultValue、SetUnit 等接口处理。",
        ],
    }


def _build_diagram_layout_guidance() -> dict[str, object]:
    """构造视图图块插入、自动布局和画布边框调整的固定顺序说明。"""
    return {
        "related_apis": _collect_api_entries(_DIAGRAM_LAYOUT_RELATED_APIS),
        "usage_patterns": [
            "固定顺序：先插入全部图块并创建全部连线，再调用 AutoLayoutDiagram(fullDiagramName)，最后调用 AdjustDiagramFrameToOptimalSize(fullDiagramName)。",
            "AdjustDiagramFrameToOptimalSize(...) 应在自动布局之后执行；导出图片时再按需调用 ExportDiagramImage(..., includeBorder=True)。",
        ],
        "recommended_snippet": (
            "AutoLayoutDiagram(diagram_full_name)\n"
            "AdjustDiagramFrameToOptimalSize(diagram_full_name)"
        ),
    }


def _build_ibd_guidance() -> dict[str, object]:
    return {
        "related_apis": _collect_api_entries(_IBD_RELATED_APIS),
        "mcp_tools": ["show_internal_properties", "run_script"],
        "usage_patterns": [
            "先创建组成属性、SetType、InsertElementToDiagram，再 ShowInternalProperties 显示类型中的子属性。",
            "内部属性仍引用类型中的原元素，无须在组成属性下创建新的语义子属性。",
            "propertyNames=None 显示全部非接口子属性；列表增量显示指定属性，已有图元和连线保留，重复调用不重复创建。",
            "parentPropertyPath 使用视图路径如 partA.child，可逐层调用继续展开；同类型的多个宿主必须各自指定路径。带点名称用单引号包裹。",
            "CreateConnectorLine / CreateBindingConnectorLine 可连接 partA.child 或 partA.child.port，嵌套属性必须先显示。",
            "完成全部图元显示和连线后调用现有 AutoLayoutDiagram，再按需 AdjustDiagramFrameToOptimalSize。",
        ],
        "recommended_snippet": (
            'ShowInternalProperties(diagram, "partA", ["child"])\n'
            'ShowInternalProperties(diagram, "partB", ["child"])\n'
            'CreateConnectorLine(diagram, "partA.child.out", "partB.child.in")\n'
            'AutoLayoutDiagram(diagram)'
        ),
    }


def _build_relation_mapping_guidance() -> dict[str, object]:
    """构造跨模型参数映射、约束计算和需求指标验证的固定顺序说明。"""
    return {
        "related_apis": _collect_api_entries(_RELATION_MAPPING_RELATED_APIS),
        "usage_patterns": [
            "CreateRelationMapping(sourceFullName, targetFullName) 的方向固定为源变量到目标变量；支持需求指标、活动输入/输出接口、块值属性，以及约束的输入/输出参数等可映射变量。",
            "建立映射前先创建两端元素，并显式统一数据类型、单位和必要的默认值；同一变量不能映射给自身。重复创建已有映射按成功处理。",
            "关系映射建立后，源端与目标端按映射保持等值；涉及约束参数时，还应检查约束满足状态。关系映射用于跨模型语义和值传递，不替代参数图内的 binding connector 或活动图内的 object flow。",
            "固定顺序：创建并配置端点 -> 设置约束表达式和参数图绑定 -> CreateRelationMapping(...) -> CalculateParametricDiagram(...) -> 读取 parameter_calculation.json。",
            "CalculateParametricDiagram(...) 不打开或切换参数图；成功时 JSON 的 values 保存层级、元素全名和数值，失败时 error 保存错误信息。验证需求指标时必须同时核对计算值、约束满足状态与 error。",
        ],
        "recommended_snippet": (
            'CreateRelationMapping("Requirements.targetOrbitAltitude", '
            '"Mission.planOrbit.targetOrbitAltitude")\n'
            'CreateRelationMapping("Mission.planOrbit.targetOrbitAltitude", '
            '"Vehicle.targetOrbitAltitude")\n'
            'CreateRelationMapping("Vehicle.targetOrbitAltitude", '
            '"Verification.altitudeConstraint.actualAltitude")\n'
            'calculation_json = CalculateParametricDiagram('
            '"Verification.AltitudeVerification.PAR")\n'
            "print(calculation_json)"
        ),
    }


def _build_team_collaboration_guidance() -> dict[str, object]:
    """构造团队登录、资源管理和仓库版本操作的安全顺序说明。"""
    return {
        "related_apis": _collect_api_entries(_TEAM_RELATED_APIS),
        "usage_patterns": [
            "优先使用 team_session、team_resources、team_repository 和 team_history 四个领域工具，通过 action 选择具体操作。",
            "team_resources 的 path 使用 ListTeamResources() 返回的可见完整路径，不包含虚拟根“我的仓库”，不需要资源 ID。",
            "提交、拉取、还原或重置前先调用 team_repository(action='status') 检查本地修改与冲突。",
            "team_repository(action='commit') 的 files 为空时提交全部变更，非空时使用仓库相对路径。",
            "delete_group、restore_files 和 reset_version 可能删除资源或丢失本地状态，必须获得用户明确确认并传 confirm=true。",
        ],
        "recommended_workflow": [
            "team_session(login) -> team_session(info) -> team_resources(list_remote)",
            "team_resources(clone_repository/clone_group) -> team_resources(list_local) -> OpenProjectFile",
            "team_repository(status) -> team_repository(commit) -> team_repository(pull) -> team_repository(push)",
            "team_history(list) -> team_history(details) -> 明确确认后 restore_files/reset_version",
        ],
        "mcp_tools": ["team_session", "team_resources", "team_repository", "team_history"],
        "preferred_mcp_tools": True,
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


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    meta={"sysbuilder": {"risk": "read"}},
)
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
    if _is_dodaf_uaf_lookup(query=query, api_name=api_name, matches=matches):
        semantic_guidance["dodaf_uaf"] = _build_dodaf_uaf_guidance()
    if _is_semantic_export_lookup(query=query, api_name=api_name, matches=matches):
        semantic_guidance["semantic_export"] = _build_semantic_export_guidance()
    if _is_architecture_tradeoff_lookup(query=query, api_name=api_name, matches=matches):
        semantic_guidance["architecture_tradeoff"] = _build_architecture_tradeoff_guidance()
    if _is_instance_lookup(query=query, api_name=api_name, matches=matches):
        semantic_guidance["instance"] = _build_instance_guidance()
    ibd_query = f"{query} {api_name}".lower()
    if any(token in ibd_query for token in (
        "ibd", "internalproperties", "内部属性", "内部结构", "嵌套属性", "组成属性", "connector",
    )) or any(str(item.get("name", "")) in _IBD_RELATED_APIS for item in matches):
        semantic_guidance["ibd_internal_properties"] = _build_ibd_guidance()
    if _is_diagram_layout_lookup(query=query, api_name=api_name, matches=matches):
        semantic_guidance["diagram_layout"] = _build_diagram_layout_guidance()
    if _is_relation_mapping_lookup(query=query, api_name=api_name, matches=matches):
        semantic_guidance["relation_mapping_and_parametric_verification"] = _build_relation_mapping_guidance()
    if _is_team_collaboration_lookup(query=query, api_name=api_name, matches=matches):
        semantic_guidance["team_collaboration"] = _build_team_collaboration_guidance()

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

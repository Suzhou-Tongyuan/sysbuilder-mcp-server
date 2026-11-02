from __future__ import annotations

import ast
import difflib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

# 独立 MCP 仓库解析 core 中同步维护的 API 源文件。
API_FILE_PATH = Path(__file__).with_name("sysbuilder_api.py")

QUERY_ALIASES: dict[str, tuple[str, ...]] = {
    "嵌套属性": ("ShowInternalProperties", "CreateConnectorLine", "CreateBindingConnectorLine"),
    "显示内部属性": ("ShowInternalProperties",),
    "显示内部结构": ("ShowInternalProperties",),
    "组成属性": ("NewPartProperty", "SetType", "InsertElementToDiagram", "ShowInternalProperties"),
    "创建项目": ("NewProject",),
    "新建项目": ("NewProject",),
    "新建工程": ("NewProject",),
    "保存项目": ("SaveProject", "SaveProjectAs"),
    "打开项目": ("OpenProjectFile",),
    "团队协同": (
        "LoginTeam",
        "ListTeamResources",
        "GetTeamRepositoryStatus",
        "CommitTeamRepository",
        "PullTeamRepository",
        "PushTeamRepository",
    ),
    "团队登录": ("LoginTeam", "GetTeamSessionInfo", "LogoutTeam"),
    "协同登录": ("LoginTeam", "GetTeamSessionInfo", "LogoutTeam"),
    "团队资源": ("ListTeamResources", "SearchPublicTeamRepositories"),
    "公共仓库": ("SearchPublicTeamRepositories",),
    "本地仓库": ("ListLocalTeamRepositories",),
    "团队分类": ("CreateTeamGroup", "UpdateTeamGroup", "DeleteTeamGroup"),
    "克隆团队仓库": ("CloneTeamRepository", "CloneTeamGroup"),
    "团队提交": ("GetTeamRepositoryStatus", "CommitTeamRepository"),
    "团队拉取": ("GetTeamRepositoryStatus", "PullTeamRepository"),
    "团队推送": ("CommitTeamRepository", "PushTeamRepository"),
    "发布团队工程": ("PublishProjectToTeam",),
    "团队提交历史": ("GetTeamRepositoryHistory", "GetTeamCommitDetails"),
    "还原团队文件": ("RestoreTeamRepositoryFiles",),
    "重置团队版本": ("ResetTeamRepositoryVersion",),
    "导入模型": ("ImportXML", "ImportReqExcel", "ImportReqIF"),
    "关系映射": ("CreateRelationMapping",),
    "需求指标映射": ("CreateRelationMapping",),
    "活动接口映射": ("CreateRelationMapping",),
    "块值属性映射": ("CreateRelationMapping",),
    "约束参数映射": ("CreateRelationMapping",),
    "参数图计算": ("CalculateParametricDiagram",),
    "约束计算": ("CalculateParametricDiagram",),
    "计算参数图": ("CalculateParametricDiagram",),
    "验证需求指标": ("CreateRelationMapping", "CalculateParametricDiagram"),
    "自动布局": ("AutoLayoutDiagram",),
    "调整画布边框": ("AdjustDiagramFrameToOptimalSize",),
    "画布边框": ("AdjustDiagramFrameToOptimalSize",),
    "视图边框": ("AdjustDiagramFrameToOptimalSize",),
    "最佳尺寸": ("AdjustDiagramFrameToOptimalSize",),
    "导出语义": ("ExportSemanticJson",),
    "语义JSON": ("ExportSemanticJson",),
    "语义树": ("ExportSemanticJson",),
    "架构权衡": ("RunArchitectureTradeoff",),
    "权衡分析": ("RunArchitectureTradeoff",),
    "新建包": ("NewPackage",),
    "新建块": ("NewBlock",),
    "新建实例": ("NewInstance",),
    "实例": ("NewInstance",),
    "新建活动": ("NewActivity",),
    "活动图": ("NewACTDiagram",),
    "状态机": ("NewStateMachine", "NewSTMDiagram"),
    "子状态": ("CreateSubState",),
    "状态迁移": ("CreateStateTransitionLine", "CreateStateTransitionLineByGraphName"),
    "需求图": ("NewREQDiagram",),
    "新建需求": ("NewRequirement",),
    "满足关系": ("CreateRequirementSatisfyLine",),
    "分配关系": ("CreateAllocateLine",),
    "对象流": ("CreateActivityObjectFlowLine", "CreateActivityObjectFlowLineByGraphName"),
    "控制流": ("CreateActivityControlFlowLine", "CreateActivityControlFlowLineByGraphName"),
    "初始节点": ("CreateActivityInitialNode", "CreateStateInitialNode"),
    "结束节点": ("CreateActivityFinalNode", "CreateStateFinalNode"),
    "DoDAF": ("NewAV1Diagram", "NewCV1aDiagram", "NewOV1aDiagram", "NewSV1aDiagram", "NewDIV1Diagram"),
    "UAF": ("NewAV1Diagram", "NewCV1aDiagram", "NewOV1aDiagram", "NewSV1aDiagram", "NewDIV1Diagram"),
    "AV视图": ("NewAV1Diagram", "NewAV2Diagram", "NewAV3Diagram"),
    "CV视图": ("NewCV1aDiagram", "NewCV1bDiagram", "NewCV2Diagram", "NewCV3Diagram", "NewCV4Diagram", "NewCV5Diagram"),
    "OV视图": ("NewOV1aDiagram", "NewOV1bDiagram", "NewOV1cDiagram", "NewOV1dDiagram", "NewOV1fDiagram", "NewOV2Diagram", "NewOV4Diagram", "NewOV5aDiagram", "NewOV5bDiagram", "NewOV6bDiagram", "NewOV6cDiagram"),
    "SV视图": ("NewSV1aDiagram", "NewSV1bDiagram", "NewSV2Diagram", "NewSV3Diagram", "NewSV4Diagram", "NewSV4bDiagram", "NewSV5aDiagram", "NewSV5bDiagram", "NewSV5cDiagram"),
    "DIV视图": ("NewDIV1Diagram",),
}


@dataclass(frozen=True)
class ApiEntry:
    name: str
    signature: str
    lineno: int
    doc_first_line: str


def _format_arg(arg: ast.arg, default: ast.AST | None = None) -> str:
    text = arg.arg
    if arg.annotation is not None:
        try:
            text += f": {ast.unparse(arg.annotation)}"
        except Exception:
            pass
    if default is not None:
        try:
            text += f" = {ast.unparse(default)}"
        except Exception:
            text += " = ..."
    return text


def _format_signature(node: ast.FunctionDef) -> str:
    parts: list[str] = []
    posonly = list(node.args.posonlyargs)
    regular = list(node.args.args)
    defaults = list(node.args.defaults)
    positional = posonly + regular
    default_start = len(positional) - len(defaults)

    for idx, arg in enumerate(positional):
        default = defaults[idx - default_start] if idx >= default_start else None
        parts.append(_format_arg(arg, default))
        if posonly and idx == len(posonly) - 1:
            parts.append("/")

    if node.args.vararg is not None:
        parts.append(f"*{_format_arg(node.args.vararg)}")
    elif node.args.kwonlyargs:
        parts.append("*")

    for kwarg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        parts.append(_format_arg(kwarg, default))

    if node.args.kwarg is not None:
        parts.append(f"**{_format_arg(node.args.kwarg)}")

    signature = f"{node.name}({', '.join(parts)})"
    if node.returns is not None:
        try:
            signature += f" -> {ast.unparse(node.returns)}"
        except Exception:
            pass
    return signature


@lru_cache(maxsize=1)
def load_api_catalog() -> tuple[ApiEntry, ...]:
    text = API_FILE_PATH.read_text(encoding="utf-8-sig", errors="ignore")
    tree = ast.parse(text)
    entries: list[ApiEntry] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name.startswith("_"):
            continue
        if node.name in {"ListFunctions", "Echo"}:
            continue
        doc = (ast.get_docstring(node) or "").strip().splitlines()
        entries.append(
            ApiEntry(
                name=node.name,
                signature=_format_signature(node),
                lineno=getattr(node, "lineno", 0) or 0,
                doc_first_line=doc[0].strip() if doc else "",
            )
        )
    return tuple(entries)


def list_api_entries() -> list[dict[str, Any]]:
    return [
        {
            "name": item.name,
            "signature": item.signature,
            "lineno": item.lineno,
            "doc_first_line": item.doc_first_line,
        }
        for item in load_api_catalog()
    ]


def get_api_names() -> set[str]:
    return {item.name for item in load_api_catalog()}


def search_api_entries(query: str = "", limit: int = 20) -> list[dict[str, Any]]:
    raw = (query or "").strip().lower()
    entries = list_api_entries()
    if not raw:
        return entries[: max(1, limit)]

    exact: list[dict[str, Any]] = []
    partial: list[dict[str, Any]] = []
    for item in entries:
        haystacks = (
            str(item["name"]).lower(),
            str(item["signature"]).lower(),
            str(item["doc_first_line"]).lower(),
        )
        if raw == haystacks[0]:
            exact.append(item)
        elif any(raw in hay for hay in haystacks):
            partial.append(item)
    return (exact + partial)[: max(1, limit)]


def suggest_api_entries(query: str = "", limit: int = 20) -> list[dict[str, Any]]:
    raw = (query or "").strip()
    entries = list_api_entries()
    capped = max(1, limit)
    if not raw:
        return entries[:capped]

    alias_hits = []
    lowered_raw = raw.lower()
    for alias, names in QUERY_ALIASES.items():
        if alias.lower() in lowered_raw:
            alias_hits.extend(names)
    if alias_hits:
        by_name = {str(item["name"]): item for item in entries}
        # 同一查询可能同时命中多个近义词，按首次出现顺序去重，避免重复返回同一 API。
        resolved = []
        seen_names: set[str] = set()
        for name in alias_hits:
            if name not in by_name or name in seen_names:
                continue
            seen_names.add(name)
            resolved.append(by_name[name])
        if resolved:
            return resolved[:capped]

    by_name = {str(item["name"]): item for item in entries}
    close_names = difflib.get_close_matches(raw, by_name.keys(), n=capped, cutoff=0.0)
    if close_names:
        return [by_name[name] for name in close_names[:capped]]

    lowered = lowered_raw
    token_hits = [
        item
        for item in entries
        if any(token and token in str(item[field]).lower() for token in lowered.replace(".", " ").replace("_", " ").split() for field in ("name", "signature", "doc_first_line"))
    ]
    if token_hits:
        return token_hits[:capped]

    return entries[:capped]


def get_api_entry(name: str) -> dict[str, Any] | None:
    raw = (name or "").strip().lower()
    if not raw:
        return None
    for item in list_api_entries():
        if str(item["name"]).lower() == raw:
            return item
    return None

from __future__ import annotations

import ast
import difflib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


API_FILE_PATH = Path(__file__).with_name("sysbuilder_api.py")

QUERY_ALIASES: dict[str, tuple[str, ...]] = {
    "创建项目": ("NewProject",),
    "新建项目": ("NewProject",),
    "新建工程": ("NewProject",),
    "保存项目": ("SaveProject", "SaveProjectAs"),
    "打开项目": ("OpenProjectFile",),
    "新建包": ("NewPackage",),
    "新建块": ("NewBlock",),
    "新建活动": ("NewActivity",),
    "活动图": ("NewACTDiagram",),
    "状态机": ("NewStateMachine", "NewSTMDiagram"),
    "状态迁移": ("CreateStateTransitionLine", "CreateStateTransitionLineByGraphName"),
    "需求图": ("NewREQDiagram",),
    "新建需求": ("NewRequirement",),
    "满足关系": ("CreateRequirementSatisfyLine",),
    "分配关系": ("CreateAllocateLine",),
    "对象流": ("CreateActivityObjectFlowLine", "CreateActivityObjectFlowLineByGraphName"),
    "控制流": ("CreateActivityControlFlowLine", "CreateActivityControlFlowLineByGraphName"),
    "初始节点": ("CreateActivityInitialNode", "CreateStateInitialNode"),
    "结束节点": ("CreateActivityFinalNode", "CreateStateFinalNode"),
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
    for alias, names in QUERY_ALIASES.items():
        if alias in raw:
            alias_hits.extend(names)
    if alias_hits:
        by_name = {str(item["name"]): item for item in entries}
        resolved = [by_name[name] for name in alias_hits if name in by_name]
        if resolved:
            return resolved[:capped]

    by_name = {str(item["name"]): item for item in entries}
    close_names = difflib.get_close_matches(raw, by_name.keys(), n=capped, cutoff=0.0)
    if close_names:
        return [by_name[name] for name in close_names[:capped]]

    lowered = raw.lower()
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

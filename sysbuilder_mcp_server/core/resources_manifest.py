"""Helpers for loading Sysbuilder resources shipped alongside the server."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from sysbuilder_mcp_server.path_config import (
    RESOURCES_MANIFEST_FILENAME,
    get_resources_root,
)

_INTERNAL_BLOCK_RE = re.compile(
    r"<!-- edition:internal:start -->.*?<!-- edition:internal:end -->",
    re.DOTALL,
)

DEFAULT_RULES_REL = "rules/default.rules"
SYSBUILDER_RULES_REL = "rules/Sysbuilder建模要求.md"
SYSBUILDER_PYTHON_API_REL = "quickref/sysbuilder_python_api.md"
SYSML_SKILL_REL = "skills/sysml-modeling-standard/SKILL.md"
SYSML_REFERENCE_REL = "skills/sysml-modeling-standard/references/SysML建模规范.md"


@dataclass(frozen=True)
class ResourceEntry:
    id: str
    name: str
    description: str
    path: str
    keywords: tuple[str, ...]


def _strip_leading_h1(text: str) -> str:
    lines = text.lstrip("\ufeff").splitlines()
    if lines and lines[0].lstrip().startswith("# "):
        return "\n".join(lines[1:]).lstrip()
    return text.strip()


def _clean_resource_text(text: str) -> str:
    cleaned = _INTERNAL_BLOCK_RE.sub("", text)
    return _strip_leading_h1(cleaned).strip()


def _as_keywords(raw: Any) -> tuple[str, ...]:
    if isinstance(raw, str):
        value = raw.strip()
        return (value,) if value else ()
    if not isinstance(raw, list):
        return ()
    values: List[str] = []
    for item in raw:
        if isinstance(item, str):
            value = item.strip()
            if value:
                values.append(value)
    return tuple(values)


def load_manifest(resources_root: Optional[Path] = None) -> Tuple[List[ResourceEntry], Path, Path]:
    root = (resources_root if resources_root is not None else get_resources_root()).resolve()
    manifest_path = root / RESOURCES_MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise FileNotFoundError(f"resources manifest not found: {manifest_path}")

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_categories = data.get("resource_categories")
    if not isinstance(raw_categories, list) or not raw_categories:
        raise ValueError("resource_categories must be a non-empty list")

    entries: List[ResourceEntry] = []
    seen_ids: set[str] = set()
    for idx, raw in enumerate(raw_categories):
        if not isinstance(raw, dict):
            raise ValueError(f"resource_categories[{idx}] must be an object")
        entry_id = str(raw.get("id", "")).strip()
        entry_name = str(raw.get("name") or raw.get("title") or entry_id).strip()
        description = str(raw.get("description", "")).strip()
        rel_path = str(raw.get("path", "")).strip().rstrip("/\\").replace("\\", "/")
        if not entry_id:
            raise ValueError(f"resource_categories[{idx}].id is required")
        if entry_id in seen_ids:
            raise ValueError(f"duplicate resource category id: {entry_id}")
        if not rel_path:
            raise ValueError(f"resource_categories[{idx}].path is required")
        seen_ids.add(entry_id)
        entries.append(
            ResourceEntry(
                id=entry_id,
                name=entry_name,
                description=description,
                path=rel_path,
                keywords=_as_keywords(raw.get("query_keywords") or raw.get("keywords")),
            )
        )
    return entries, manifest_path, root


def browse_resources_manifest_for_instructions(
    resources_root: Optional[Path] = None,
) -> Tuple[str, Dict[str, Any]]:
    root = (resources_root if resources_root is not None else get_resources_root()).resolve()
    manifest_path = root / RESOURCES_MANIFEST_FILENAME
    meta: Dict[str, Any] = {
        "ok": False,
        "resources_root": str(root),
        "manifest_path": str(manifest_path),
        "categories": 0,
        "error": None,
    }
    if not manifest_path.is_file():
        meta["error"] = "manifest_missing"
        return (
            "\n## Sysbuilder Resources\n\n"
            f"未找到 `{RESOURCES_MANIFEST_FILENAME}`，预期路径：`{manifest_path}`。\n",
            meta,
        )

    try:
        entries, _, _ = load_manifest(root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        meta["error"] = f"manifest_invalid: {exc}"
        return (
            "\n## Sysbuilder Resources\n\n"
            f"`{manifest_path}` 无法读取或解析：{exc}\n",
            meta,
        )

    meta["ok"] = True
    meta["categories"] = len(entries)
    lines = [
        "",
        "## Sysbuilder Resources",
        "",
        f"- 资源根目录：`{root}`",
        f"- 清单文件：`{manifest_path}`",
        "- 启动时会注入关键规则摘要；详细内容请按需查阅对应资源文件。",
        "",
    ]
    for entry in entries:
        lines.append(f"### `{entry.id}`")
        if entry.description:
            lines.append(f"- {entry.description}")
        lines.append(f"- 路径：`{entry.path}`")
        if entry.keywords:
            lines.append(f"- 适用主题：{', '.join(entry.keywords[:10])}")
        lines.append("")
    return "\n".join(lines), meta


def _extract_before_heading(body: str, heading_prefix: str) -> str:
    marker = f"\n{heading_prefix}"
    if marker in body:
        return body.split(marker, 1)[0].rstrip()
    return body.strip()


def _load_text_fragment(
    *,
    relative_path: str,
    section_title: str,
    intro: str,
    max_bytes: int = 256_000,
    extractor: Optional[Callable[[str], str]] = None,
    resources_root: Optional[Path] = None,
) -> Tuple[str, Dict[str, Any]]:
    root = (resources_root if resources_root is not None else get_resources_root()).resolve()
    path = (root / relative_path.replace("\\", "/")).resolve()
    meta: Dict[str, Any] = {
        "ok": False,
        "resources_root": str(root),
        "path": str(path),
        "error": None,
        "size_bytes": 0,
    }

    try:
        path.relative_to(root)
    except ValueError:
        meta["error"] = "path_escape"
        return f"\n## {section_title}\n\n资源路径异常：`{path}`\n", meta

    if not path.is_file():
        meta["error"] = "missing"
        return f"\n## {section_title}\n\n未找到资源文件：`{path}`\n", meta

    try:
        size_bytes = path.stat().st_size
        if size_bytes > max_bytes:
            meta["error"] = f"file_too_large:{size_bytes}"
            return f"\n## {section_title}\n\n资源文件过大，已跳过注入：`{path}`\n", meta
        body = _clean_resource_text(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        meta["error"] = f"read_error: {exc}"
        return f"\n## {section_title}\n\n无法读取资源文件：`{path}`\n", meta

    if extractor is not None:
        body = extractor(body).strip()

    meta["ok"] = True
    meta["size_bytes"] = len(body.encode("utf-8"))
    fragment = (
        f"\n## {section_title}\n\n"
        f"{intro}\n\n"
        f"{body}\n"
    )
    return fragment, meta


def load_default_rules_for_instructions(
    resources_root: Optional[Path] = None,
) -> Tuple[str, Dict[str, Any]]:
    return _load_text_fragment(
        relative_path=DEFAULT_RULES_REL,
        section_title="Workspace Rules",
        intro="以下摘要来自 `resources/rules/default.rules`，表示工作区级硬性执行约束。",
        max_bytes=32_000,
        resources_root=resources_root,
    )


def load_sysbuilder_rules_for_instructions(
    resources_root: Optional[Path] = None,
) -> Tuple[str, Dict[str, Any]]:
    return _load_text_fragment(
        relative_path=SYSBUILDER_RULES_REL,
        section_title="Sysbuilder Modeling Rules",
        intro=(
            "以下摘要来自 `resources/rules/Sysbuilder建模要求.md`，涉及 Sysbuilder 建模、脚本编码、"
            "视图与追溯要求，执行前必须遵守。`run_script` 运行时会自动注入 "
            "`MODELING_RULES`、`GetModelingRuleText()`、`PrintModelingRuleSummary()` "
            "供建模脚本直接读取。"
        ),
        max_bytes=96_000,
        resources_root=resources_root,
    )


def load_sysml_skill_for_instructions(
    resources_root: Optional[Path] = None,
) -> Tuple[str, Dict[str, Any]]:
    return _load_text_fragment(
        relative_path=SYSML_SKILL_REL,
        section_title="SysML Skill Entry",
        intro="以下技能入口定义了在本工作区做 SysML / Sysbuilder 任务时应优先遵循的工作流。",
        max_bytes=48_000,
        resources_root=resources_root,
    )


def load_sysbuilder_python_api_for_instructions(
    resources_root: Optional[Path] = None,
) -> Tuple[str, Dict[str, Any]]:
    return _load_text_fragment(
        relative_path=SYSBUILDER_PYTHON_API_REL,
        section_title="Sysbuilder Python API Quick Reference",
        intro=(
            "以下摘要来自 `resources/quickref/sysbuilder_python_api.md`，用于提供 Sysbuilder Python 自动建模脚本的 "
            "API 速查、图种兼容性说明与常用建模片段参考。"
        ),
        max_bytes=96_000,
        resources_root=resources_root,
    )


def load_sysml_reference_for_instructions(
    resources_root: Optional[Path] = None,
) -> Tuple[str, Dict[str, Any]]:
    return _load_text_fragment(
        relative_path=SYSML_REFERENCE_REL,
        section_title="SysML Reference Rules",
        intro="以下摘要来自 `resources/skills/sysml-modeling-standard/references/SysML建模规范.md`，用于约束命名、图种选择、关系与追溯方式。",
        extractor=lambda body: _extract_before_heading(body, "## 4. 模型元素使用规范"),
        max_bytes=96_000,
        resources_root=resources_root,
    )


def load_runtime_resource_texts(resources_root: Optional[Path] = None) -> Dict[str, str]:
    root = (resources_root if resources_root is not None else get_resources_root()).resolve()
    result: Dict[str, str] = {}
    for key, rel_path in (
        ("default_rules", DEFAULT_RULES_REL),
        ("sysbuilder_rules", SYSBUILDER_RULES_REL),
        ("sysbuilder_python_api", SYSBUILDER_PYTHON_API_REL),
        ("sysml_skill", SYSML_SKILL_REL),
        ("sysml_reference", SYSML_REFERENCE_REL),
    ):
        path = root / rel_path
        try:
            result[key] = _clean_resource_text(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            result[key] = ""
    return result


def _summarize_resource_text(text: str, max_lines: int = 12) -> str:
    if not text.strip():
        return ""
    lines: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        lines.append(line)
        if len(lines) >= max_lines:
            break
    return "\n".join(lines)


def load_runtime_resource_bundle(resources_root: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    root = (resources_root if resources_root is not None else get_resources_root()).resolve()
    bundle: Dict[str, Dict[str, Any]] = {}
    for key, rel_path in (
        ("default_rules", DEFAULT_RULES_REL),
        ("sysbuilder_rules", SYSBUILDER_RULES_REL),
        ("sysbuilder_python_api", SYSBUILDER_PYTHON_API_REL),
        ("sysml_skill", SYSML_SKILL_REL),
        ("sysml_reference", SYSML_REFERENCE_REL),
    ):
        path = (root / rel_path).resolve()
        text = ""
        ok = False
        error = ""
        try:
            text = _clean_resource_text(path.read_text(encoding="utf-8"))
            ok = True
        except (OSError, UnicodeError) as exc:
            error = str(exc)
        bundle[key] = {
            "key": key,
            "path": str(path),
            "ok": ok,
            "error": error,
            "text": text,
            "summary": _summarize_resource_text(text),
        }
    return bundle

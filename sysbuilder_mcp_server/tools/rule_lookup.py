"""Sysbuilder modeling rule lookup MCP tool."""
from __future__ import annotations

import re
from typing import Any

from sysbuilder_mcp_server.core.resources_manifest import load_runtime_resource_bundle
from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.tools.common import _json


def _score_line(line: str, query: str) -> int:
    raw = (query or "").strip().lower()
    text = (line or "").strip().lower()
    if not raw or not text:
        return 0
    score = 0
    if raw in text:
        score += 100
    tokens = [token for token in re.split(r"[\s,.;:|/\\_\-\[\]\(\)]+", raw) if token]
    for token in tokens:
        if token in text:
            score += 10
    return score


def _search_text(text: str, query: str, max_hits: int) -> list[dict[str, Any]]:
    lines = text.splitlines()
    hits: list[dict[str, Any]] = []
    for idx, line in enumerate(lines):
        score = _score_line(line, query)
        if score <= 0:
            continue
        context_start = max(0, idx - 1)
        context_end = min(len(lines), idx + 2)
        snippet = "\n".join(lines[context_start:context_end]).strip()
        hits.append(
            {
                "lineno": idx + 1,
                "score": score,
                "line": line.strip(),
                "snippet": snippet,
            }
        )
    hits.sort(key=lambda item: (-int(item["score"]), int(item["lineno"])))
    return hits[:max_hits]


@mcp.tool()
def lookup_sysbuilder_rules(
    query: str,
    sources: list[str] | None = None,
    limit: int = 12,
) -> str:
    """
    查询 Sysbuilder 建模规则与 quickref 文本，适合查活动图、状态机、IBD、追溯、参数图等执行约束。

    `sources` 可选值：
    - `sysbuilder_rules`
    - `sysbuilder_python_api`
    - `sysml_reference`
    - `sysml_skill`
    - `default_rules`
    """
    bundle = load_runtime_resource_bundle()
    allowed = {"sysbuilder_rules", "sysbuilder_python_api", "sysml_reference", "sysml_skill", "default_rules"}
    chosen_sources = [item for item in (sources or ["sysbuilder_rules", "sysbuilder_python_api"]) if item in allowed]
    if not chosen_sources:
        chosen_sources = ["sysbuilder_rules", "sysbuilder_python_api"]

    capped_limit = min(max(limit or 12, 1), 50)
    per_source_limit = max(1, capped_limit)
    results: list[dict[str, Any]] = []
    for source_key in chosen_sources:
        entry = bundle.get(source_key) or {}
        text = str(entry.get("text", "") or "")
        if not text.strip():
            continue
        hits = _search_text(text=text, query=query, max_hits=per_source_limit)
        if not hits:
            continue
        results.append(
            {
                "source": source_key,
                "path": str(entry.get("path", "")),
                "match_count": len(hits),
                "matches": hits,
            }
        )

    total_hits = sum(int(item["match_count"]) for item in results)
    return _json(
        {
            "ok": True,
            "tool": "lookup_sysbuilder_rules",
            "query": (query or "").strip(),
            "sources": chosen_sources,
            "source_count": len(results),
            "total_hits": total_hits,
            "results": results,
            "hint": (
                "No matching rule text was found in the selected sources."
                if total_hits == 0
                else "Matched rule snippets from Sysbuilder modeling resources."
            ),
            "recommended_workflow": [
                "先用 lookup_sysbuilder_rules 查执行约束，再用 lookup_sysbuilder_api 查接口。",
                "需要写脚本时，先锁定规则和 API，再一次性生成完整脚本。",
            ],
        }
    )

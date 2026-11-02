"""Search and page-reading helpers for the packaged Sysbuilder user manual index."""
from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

from sysbuilder_mcp_server.path_config import get_resources_root


MANUAL_INDEX_RELATIVE_PATH = "manuals/Sysbuilder_User_Manual.pages.json"
_QUESTION_WORDS = (
    "请问",
    "请告诉我",
    "告诉我",
    "帮我",
    "怎么",
    "怎样",
    "如何",
    "能否",
    "可以",
    "一下",
    "使用说明",
    "使用方法",
    "操作方法",
)
_HEADING_RE = re.compile(r"^\d+(?:\.\d+)*\s+\S+")


def _normalize(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").casefold()
    return re.sub(r"\s+", " ", text).strip()


def _query_terms(query: str) -> tuple[str, list[str]]:
    normalized = _normalize(query)
    reduced = normalized
    for word in _QUESTION_WORDS:
        reduced = reduced.replace(word, " ")
    chunks = re.findall(r"[a-z0-9_.+\-]+|[\u3400-\u9fff]+", reduced)
    terms: list[str] = []
    for chunk in chunks:
        if chunk not in terms:
            terms.append(chunk)
        if re.fullmatch(r"[\u3400-\u9fff]+", chunk) and len(chunk) >= 4:
            for width in (2, 3):
                for index in range(0, len(chunk) - width + 1):
                    gram = chunk[index : index + width]
                    if gram not in terms:
                        terms.append(gram)
    return normalized, terms


@lru_cache(maxsize=8)
def _load_index_file(path_text: str) -> dict[str, Any]:
    path = Path(path_text)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("format_version") != 1 or not isinstance(payload.get("pages"), list):
        raise ValueError(f"unsupported manual index format: {path}")
    return payload


def _index_path(resources_root: Path | None = None) -> Path:
    root = (resources_root or get_resources_root()).resolve()
    path = (root / MANUAL_INDEX_RELATIVE_PATH).resolve()
    path.relative_to(root)
    return path


def load_manual_index(resources_root: Path | None = None) -> tuple[dict[str, Any], Path]:
    path = _index_path(resources_root)
    if not path.is_file():
        raise FileNotFoundError(f"Sysbuilder help manual index not found: {path}")
    return _load_index_file(str(path)), path


def _score_text(text: str, normalized_query: str, terms: list[str]) -> int:
    normalized_text = _normalize(text)
    if not normalized_text:
        return 0
    score = 0
    if normalized_query and normalized_query in normalized_text:
        score += 240
    for term in terms:
        count = normalized_text.count(term)
        if count:
            score += min(count, 5) * (len(term) * 4 + (32 if len(term) >= 4 else 4))
    return score


def _best_snippet(text: str, normalized_query: str, terms: list[str], max_chars: int = 1400) -> tuple[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "", ""
    best_index = max(range(len(lines)), key=lambda index: _score_text(lines[index], normalized_query, terms))
    start = max(0, best_index - 2)
    end = min(len(lines), best_index + 4)
    snippet = "\n".join(lines[start:end])[:max_chars].strip()
    heading = ""
    for index in range(best_index, -1, -1):
        if _HEADING_RE.match(lines[index]):
            heading = lines[index]
            break
    return snippet, heading


def search_manual(query: str, limit: int = 8, resources_root: Path | None = None) -> dict[str, Any]:
    normalized_query, terms = _query_terms(query)
    if not normalized_query or not terms:
        return {"ok": False, "error": "query_required", "query": query or ""}
    try:
        payload, index_path = load_manual_index(resources_root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return {"ok": False, "error": "manual_index_unavailable", "message": str(exc)}

    hits: list[dict[str, Any]] = []
    for entry in payload["pages"]:
        if not isinstance(entry, dict):
            continue
        text = str(entry.get("text", "") or "")
        score = _score_text(text, normalized_query, terms)
        if score <= 0:
            continue
        snippet, heading = _best_snippet(text, normalized_query, terms)
        hits.append(
            {
                "page": int(entry.get("page", 0) or 0),
                "heading": heading,
                "score": score,
                "snippet": snippet,
            }
        )
    hits.sort(key=lambda item: (-int(item["score"]), int(item["page"])))
    capped_limit = min(max(int(limit or 8), 1), 20)
    return {
        "ok": True,
        "tool": "search_sysbuilder_help",
        "manual": str(payload.get("title", "MWORKS.Sysbuilder 用户手册")),
        "source_pdf": str(payload.get("source_pdf", "Sysbuilder_User_Manual.pdf")),
        "index_path": str(index_path),
        "query": query.strip(),
        "total_matching_pages": len(hits),
        "results": hits[:capped_limit],
        "answer_guidance": "根据命中页回答并标注 PDF 页码；细节不足时调用 read_sysbuilder_help_pages。",
    }


def read_manual_pages(
    start_page: int,
    end_page: int | None = None,
    resources_root: Path | None = None,
) -> dict[str, Any]:
    try:
        payload, index_path = load_manual_index(resources_root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return {"ok": False, "error": "manual_index_unavailable", "message": str(exc)}

    page_count = int(payload.get("page_count", len(payload["pages"])))
    first = int(start_page)
    last = int(end_page if end_page is not None else start_page)
    if first < 1 or last < first or last > page_count:
        return {
            "ok": False,
            "error": "invalid_page_range",
            "page_count": page_count,
            "requested": [first, last],
        }
    if last - first + 1 > 5:
        return {
            "ok": False,
            "error": "page_range_too_large",
            "message": "一次最多读取 5 页。",
            "requested": [first, last],
        }

    by_page = {
        int(entry.get("page", 0)): str(entry.get("text", "") or "")
        for entry in payload["pages"]
        if isinstance(entry, dict)
    }
    pages = [{"page": page, "text": by_page.get(page, "")} for page in range(first, last + 1)]
    return {
        "ok": True,
        "tool": "read_sysbuilder_help_pages",
        "manual": str(payload.get("title", "MWORKS.Sysbuilder 用户手册")),
        "source_pdf": str(payload.get("source_pdf", "Sysbuilder_User_Manual.pdf")),
        "index_path": str(index_path),
        "page_count": page_count,
        "pages": pages,
        "citation_guidance": "回答时请标注所依据的 PDF 页码。",
    }

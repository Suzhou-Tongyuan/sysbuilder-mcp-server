"""Read-only MCP tools for answering Sysbuilder usage questions from the packaged manual."""
from __future__ import annotations

from sysbuilder_mcp_server.help_manual_index import read_manual_pages, search_manual
from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.tools.common import _json


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    meta={"sysbuilder": {"risk": "read"}},
)
def search_sysbuilder_help(query: str, limit: int = 8) -> str:
    """
    搜索《MWORKS.Sysbuilder 用户手册》，用于回答界面操作、建模步骤、菜单、快捷键和功能说明。

    返回相关 PDF 页码及原文片段。回答前应优先使用命中内容，并在答案中标注手册页码。
    """
    return _json(search_manual(query=query, limit=limit))


@mcp.tool(
    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    meta={"sysbuilder": {"risk": "read"}},
)
def read_sysbuilder_help_pages(start_page: int, end_page: int | None = None) -> str:
    """读取《MWORKS.Sysbuilder 用户手册》的指定 PDF 页，一次最多读取连续 5 页。"""
    return _json(read_manual_pages(start_page=start_page, end_page=end_page))

"""验证 SysML v1 单文件 MCP 的内嵌规则、API 目录和工具发现。"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def payload(result):
    assert not result.isError, result
    return json.loads(next(item.text for item in result.content if hasattr(item, "text")))


async def run(executable):
    params = StdioServerParameters(command=str(executable.resolve()), args=[])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            assert "9.2 嵌套属性与显示内部属性" in initialized.instructions
            assert "ShowInternalProperties" in initialized.instructions
            listing = await session.list_tools()
            tools = {tool.name for tool in listing.tools}
            assert "show_internal_properties" in tools
            rules = payload(await session.call_tool("lookup_sysbuilder_rules", {
                "query": "ShowInternalProperties", "sources": ["sysbuilder_rules"],
            }))
            assert rules["total_hits"] > 0, rules
            assert "ShowInternalProperties" in json.dumps(rules, ensure_ascii=False)
            api = payload(await session.call_tool("lookup_sysbuilder_api", {
                "api_name": "ShowInternalProperties",
            }))
            assert api["matches"][0]["name"] == "ShowInternalProperties", api
            guidance = api["semantic_guidance"]["ibd_internal_properties"]
            assert "AutoLayoutDiagram" in guidance["recommended_snippet"]
            print(json.dumps({"ok": True, "executable": str(executable.resolve()),
                              "tool_count": len(tools), "embedded_rules": True,
                              "nested_property_api": True}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    args = parser.parse_args()
    asyncio.run(run(args.executable))

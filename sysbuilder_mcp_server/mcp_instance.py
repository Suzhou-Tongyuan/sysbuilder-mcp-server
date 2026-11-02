"""Sysbuilder MCP Server FastMCP singleton."""
from __future__ import annotations

import logging

from sysbuilder_mcp_server.path_config import get_output_root, get_resources_root, get_workspace_root

try:
    from mcp.server.fastmcp import FastMCP

    _FASTMCP_AVAILABLE = True
except ImportError:
    _FASTMCP_AVAILABLE = False

    class FastMCP:  # type: ignore[override]
        def __init__(self, _name: str, instructions: str | None = None) -> None:
            self._name = _name
            self.instructions = instructions

        def tool(self, *args, **kwargs):
            def _decorator(func):
                return func

            return _decorator

        def run(self) -> None:
            raise RuntimeError("FastMCP not installed")

_log = logging.getLogger(__name__)

_BASE_INSTRUCTIONS = (
    "You are using the Sysbuilder MCP server.\n"
    "Prefer the dedicated Sysbuilder MCP tools over inventing unsupported helper APIs.\n"
    "Before any Sysbuilder modeling task, first read `resources/rules/Sysbuilder建模要求.md`.\n"
    "Before any Sysbuilder scripting task, also read `resources/quickref/sysbuilder_python_api.md`.\n"
    "When SYSML_V1_API_PORT is present, connect only to that embedded Sysbuilder instance and never start or select another instance.\n"
    "Outside embedded mode, a new modeling session may start a new Sysbuilder instance directly.\n"
    "After a successful `start(...)`, continue modeling directly and do not call `find()` or `connect()` again unless the user explicitly asks to inspect or connect to an existing instance.\n"
    "For Sysbuilder modeling-rule questions, query rule text with lookup_sysbuilder_rules when needed.\n"
    "For Sysbuilder product usage, UI, menu, shortcut, or how-to questions, first call search_sysbuilder_help; read the relevant pages with read_sysbuilder_help_pages when more context is needed, and cite PDF page numbers in the answer.\n"
    "For Sysbuilder scripting tasks, query APIs with lookup_sysbuilder_api before writing the full script.\n"
    "Store intermediate data under the configured output root, which defaults to the user's `Sysbuilder/SysMLAIOutput` directory.\n"
    "Tool metadata exposes `meta.sysbuilder.risk` as read, write, or destructive; run_script additionally classifies its script dynamically.\n"
    "For team collaboration, use team_session, team_resources, team_repository, and team_history with the documented action values.\n"
    "Login with team_session before accessing remote team resources.\n"
    "Inspect team repository status before commit, pull, restore, or reset operations. Never expose team passwords in responses or logs.\n"
    "Delete, restore, and reset tools require confirm=true after the user explicitly confirms the destructive operation.\n"
)

try:
    from sysbuilder_mcp_server.core.resources_manifest import (
        browse_resources_manifest_for_instructions,
        load_default_rules_for_instructions,
        load_sysbuilder_python_api_for_instructions,
        load_sysbuilder_rules_for_instructions,
        load_sysml_reference_for_instructions,
        load_sysml_skill_for_instructions,
    )
except Exception:
    _PATH_HINT = ""
    _DEFAULT_RULES_FRAG = "\n## Workspace Rules\n\n（resources loader 未成功加载）\n"
    _DEFAULT_RULES_META: dict[str, object] = {"ok": False, "error": "import_failed"}
    _SYSBUILDER_RULES_FRAG = "\n## Sysbuilder Modeling Rules\n\n（resources loader 未成功加载）\n"
    _SYSBUILDER_RULES_META: dict[str, object] = {"ok": False, "error": "import_failed"}
    _SYSBUILDER_PYTHON_API_FRAG = "\n## Sysbuilder Python API Quick Reference\n\n（resources loader 未成功加载）\n"
    _SYSBUILDER_PYTHON_API_META: dict[str, object] = {"ok": False, "error": "import_failed"}
    _SYSML_SKILL_FRAG = "\n## SysML Skill Entry\n\n（resources loader 未成功加载）\n"
    _SYSML_SKILL_META: dict[str, object] = {"ok": False, "error": "import_failed"}
    _SYSML_REF_FRAG = "\n## SysML Reference Rules\n\n（resources loader 未成功加载）\n"
    _SYSML_REF_META: dict[str, object] = {"ok": False, "error": "import_failed"}
    _DOC_CORPORA_FRAG = "\n## Sysbuilder Resources\n\n（resources manifest 未成功加载）\n"
    _DOC_CORPORA_META: dict[str, object] = {"ok": False, "error": "import_failed"}
else:
    _PATH_HINT = (
        "\n## Paths\n\n"
        f"- Workspace root: `{get_workspace_root()}`\n"
        f"- Resources root: `{get_resources_root()}`\n"
        f"- Intermediate data root: `{get_output_root()}`\n"
        "- 若资源目录不在默认位置，请通过 `MCP_RESOURCES_DIR` 或 `--resources-dir` 显式指定。\n"
        "- 中间数据目录可通过 `MCP_OUTPUT_DIR` 或 `--output-dir` 显式覆盖。\n"
    )
    _DEFAULT_RULES_FRAG, _DEFAULT_RULES_META = load_default_rules_for_instructions()
    _SYSBUILDER_RULES_FRAG, _SYSBUILDER_RULES_META = load_sysbuilder_rules_for_instructions()
    _SYSBUILDER_PYTHON_API_FRAG, _SYSBUILDER_PYTHON_API_META = load_sysbuilder_python_api_for_instructions()
    _SYSML_SKILL_FRAG, _SYSML_SKILL_META = load_sysml_skill_for_instructions()
    _SYSML_REF_FRAG, _SYSML_REF_META = load_sysml_reference_for_instructions()
    _DOC_CORPORA_FRAG, _DOC_CORPORA_META = browse_resources_manifest_for_instructions()

    for label, meta in (
        ("workspace rules", _DEFAULT_RULES_META),
        ("sysbuilder modeling rules", _SYSBUILDER_RULES_META),
        ("sysbuilder python api quick reference", _SYSBUILDER_PYTHON_API_META),
        ("sysml skill entry", _SYSML_SKILL_META),
        ("sysml reference rules", _SYSML_REF_META),
        ("sysbuilder resources manifest", _DOC_CORPORA_META),
    ):
        if meta.get("ok"):
            _log.info("loaded %s from %s", label, meta.get("path", meta.get("manifest_path")))
        else:
            _log.warning("failed to load %s: %s", label, meta.get("error"))


mcp = FastMCP(
    "sysbuilder_mcp",
    instructions=(
        _BASE_INSTRUCTIONS
        + _PATH_HINT
        + _DEFAULT_RULES_FRAG
        + _SYSBUILDER_RULES_FRAG
        + _SYSBUILDER_PYTHON_API_FRAG
        + _SYSML_SKILL_FRAG
        + _SYSML_REF_FRAG
        + _DOC_CORPORA_FRAG
    ),
)

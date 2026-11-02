from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _apply_env_from_argv() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--sysbuilder-install-dir", type=str, default=None)
    parser.add_argument("--sysml-v1-install-dir", type=str, default=None)
    parser.add_argument("--sysml-v1-api-host", type=str, default=None)
    parser.add_argument("--sysml-v1-api-port", type=int, default=None)
    parser.add_argument("--sysbuilder-process-path", type=str, default=None)
    parser.add_argument("--resources-dir", type=str, default=None)
    parser.add_argument("--workspace-dir", type=str, default=None)
    parser.add_argument("--sysbuilder-workspace", type=str, default=None)
    parser.add_argument("--output-dir", type=str, default=None)
    args, _ = parser.parse_known_args()

    install_dir = args.sysml_v1_install_dir or args.sysbuilder_install_dir
    if install_dir:
        os.environ["SYSML_V1_INSTALL_DIR"] = install_dir.strip()
    if args.sysml_v1_api_host:
        os.environ["SYSML_V1_API_HOST"] = args.sysml_v1_api_host.strip()
    if args.sysml_v1_api_port:
        os.environ["SYSML_V1_API_PORT"] = str(args.sysml_v1_api_port)
    if args.sysbuilder_process_path:
        os.environ["SYSBUILDER_PROCESS_PATH"] = args.sysbuilder_process_path.strip()
    if args.resources_dir:
        os.environ["MCP_RESOURCES_DIR"] = args.resources_dir.strip()
    workspace_dir = args.sysbuilder_workspace or args.workspace_dir
    if workspace_dir:
        os.environ["SYSBUILDER_WORKSPACE_DIR"] = workspace_dir.strip()
    if args.output_dir:
        os.environ["MCP_OUTPUT_DIR"] = args.output_dir.strip()


_apply_env_from_argv()

from sysbuilder_mcp_server.mcp_instance import _FASTMCP_AVAILABLE, mcp  # noqa: E402
import sysbuilder_mcp_server.tools.api_lookup  # noqa: F401,E402
import sysbuilder_mcp_server.tools.architecture_tradeoff  # noqa: F401,E402
import sysbuilder_mcp_server.tools.geometry_docs  # noqa: F401,E402
import sysbuilder_mcp_server.tools.help_manual  # noqa: F401,E402
import sysbuilder_mcp_server.tools.ibd  # noqa: F401,E402
import sysbuilder_mcp_server.tools.model_import  # noqa: F401,E402
import sysbuilder_mcp_server.tools.modelica  # noqa: F401,E402
import sysbuilder_mcp_server.tools.parametric_verification  # noqa: F401,E402
import sysbuilder_mcp_server.tools.report  # noqa: F401,E402
import sysbuilder_mcp_server.tools.rule_lookup  # noqa: F401,E402
import sysbuilder_mcp_server.tools.run_script  # noqa: F401,E402
import sysbuilder_mcp_server.tools.semantic_json  # noqa: F401,E402
import sysbuilder_mcp_server.tools.session_tools  # noqa: F401,E402
import sysbuilder_mcp_server.tools.team_collaboration  # noqa: F401,E402
import sysbuilder_mcp_server.tools.traceability  # noqa: F401,E402
from sysbuilder_mcp_server.version import format_version_banner  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Sysbuilder MCP Server")
    parser.add_argument("--sysbuilder-install-dir", type=str, help="Path to Sysbuilder installation directory")
    parser.add_argument("--sysml-v1-install-dir", type=str, help="Canonical SysML v1 installation directory")
    parser.add_argument("--sysml-v1-api-host", type=str, help="Current SysML v1 ScriptService host")
    parser.add_argument("--sysml-v1-api-port", type=int, help="Current SysML v1 ScriptService port")
    parser.add_argument("--sysbuilder-process-path", type=str, help="Path to Sysbuilder.exe")
    parser.add_argument("--resources-dir", type=str, help="Resources directory")
    parser.add_argument("--workspace-dir", type=str, help="Workspace directory")
    parser.add_argument("--sysbuilder-workspace", type=str, help="Canonical SysBuilder workspace directory")
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Intermediate data directory (default: ~/Sysbuilder/SysMLAIOutput)",
    )

    if any(arg in ("--version", "-V") for arg in sys.argv[1:]):
        print(format_version_banner(), file=sys.stderr)
        return 0

    parser.parse_args()

    if not _FASTMCP_AVAILABLE:
        print("FastMCP not found. Install with: pip install mcp", file=sys.stderr)
        return 1

    print(format_version_banner(), file=sys.stderr)
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

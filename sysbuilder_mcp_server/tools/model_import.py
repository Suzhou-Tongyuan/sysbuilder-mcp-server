"""Sysbuilder model import MCP tool."""
from __future__ import annotations

from pathlib import Path

from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.path_config import get_workspace_root
from sysbuilder_mcp_server.core import ImportReqExcel, ImportReqIF, ImportXML
from sysbuilder_mcp_server.tools.common import _json, capture_python_output, ensure_sysbuilder_session


def _resolve_input_path(path: str) -> Path:
    raw = (path or "").strip()
    if not raw:
        raise ValueError("input_path cannot be empty.")
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = (get_workspace_root() / candidate).resolve()
    return candidate


def _normalize_import_type(import_type: str, path: Path) -> tuple[str, str]:
    raw = (import_type or "auto").strip().lower()
    suffix = path.suffix.lower()

    if raw == "auto":
        if suffix in (".xlsx", ".xls"):
            return "excel", "ImportReqExcel"
        if suffix in (".reqif", ".reqifz"):
            return "reqif", "ImportReqIF"
        if suffix == ".xml":
            return "xml", "ImportXML"
        raise ValueError(f"Cannot infer import type from suffix: {suffix or '<none>'}")

    aliases = {
        "excel": ("excel", "ImportReqExcel"),
        "req_excel": ("excel", "ImportReqExcel"),
        "xlsx": ("excel", "ImportReqExcel"),
        "reqif": ("reqif", "ImportReqIF"),
        "reqifz": ("reqif", "ImportReqIF"),
        "xml": ("xml", "ImportXML"),
    }
    if raw not in aliases:
        raise ValueError("import_type must be one of auto|excel|reqif|xml")
    return aliases[raw]


@mcp.tool()
def import_model(
    input_path: str,
    import_type: str = "auto",
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    导入外部模型或需求文件到 Sysbuilder。

    支持：
    - 需求 Excel：`.xlsx` / `.xls`
    - ReqIF：`.reqif` / `.reqifz`
    - XML：`.xml`

    `import_type` 可传 `auto` 自动识别，也可显式指定 `excel` / `reqif` / `xml`。
    """
    try:
        resolved_input = _resolve_input_path(input_path)
    except ValueError as exc:
        return _json(
            {
                "ok": False,
                "tool": "import_model",
                "error": str(exc),
            }
        )

    if not resolved_input.is_file():
        return _json(
            {
                "ok": False,
                "tool": "import_model",
                "error": f"input_path is not a file: {resolved_input}",
            }
        )

    try:
        normalized_type, api_name = _normalize_import_type(import_type, resolved_input)
    except ValueError as exc:
        return _json(
            {
                "ok": False,
                "tool": "import_model",
                "error": str(exc),
                "input_path": str(resolved_input),
            }
        )

    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "import_model",
                "error": "Failed to start or connect Sysbuilder.",
                "input_path": str(resolved_input),
                "import_type": normalized_type,
                "api": api_name,
                "session": session,
            }
        )

    with capture_python_output() as (buf_out, buf_err):
        if normalized_type == "excel":
            result = ImportReqExcel(str(resolved_input))
        elif normalized_type == "reqif":
            result = ImportReqIF(str(resolved_input))
        else:
            result = ImportXML(str(resolved_input))

    return _json(
        {
            "ok": bool(result),
            "tool": "import_model",
            "input_path": str(resolved_input),
            "import_type": normalized_type,
            "api": api_name,
            "result": result,
            "session": session,
            "stdout": buf_out.getvalue(),
            "stderr": buf_err.getvalue(),
        }
    )

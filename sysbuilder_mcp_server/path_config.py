from __future__ import annotations

import os
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
DEPLOY_ROOT = PACKAGE_ROOT
WORKSPACE_ROOT = Path(
    os.environ.get("SYSBUILDER_WORKSPACE_DIR")
    or os.environ.get("MCP_WORKSPACE_DIR")
    or PROJECT_ROOT
).resolve()
RESOURCES_ROOT = Path(os.environ.get("MCP_RESOURCES_DIR") or (PROJECT_ROOT / "resources")).resolve()
OUTPUT_ROOT = Path(
    os.environ.get("MCP_OUTPUT_DIR") or (Path.home() / "Sysbuilder" / "SysMLAIOutput")
).resolve()
RESOURCES_MANIFEST_FILENAME = "resources_manifest.json"


def get_workspace_root() -> Path:
    return WORKSPACE_ROOT


def get_resources_root() -> Path:
    return RESOURCES_ROOT


def get_resources_manifest_path() -> Path:
    return get_resources_root() / RESOURCES_MANIFEST_FILENAME


def get_output_root() -> Path:
    """返回中间数据根目录，并在首次使用时确保目录存在。"""
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    return OUTPUT_ROOT


def get_sysbuilder_install_dir() -> Path | None:
    raw = (
        os.environ.get("SYSML_V1_INSTALL_DIR")
        or os.environ.get("SYSBUILDER_INSTALL_DIR")
        or ""
    ).strip()
    if not raw:
        return None
    return Path(raw).expanduser().resolve()


def get_sysbuilder_process_path() -> Path | None:
    raw_process = (os.environ.get("SYSBUILDER_PROCESS_PATH") or "").strip()
    if raw_process:
        process_path = Path(raw_process).expanduser().resolve()
        if process_path.is_dir():
            candidates = (
                process_path / "Bin" / "Sysbuilder.exe",
                process_path / "Sysbuilder.exe",
            )
            for candidate in candidates:
                if candidate.exists():
                    return candidate.resolve()
        return process_path

    install_dir = get_sysbuilder_install_dir()
    if install_dir is None:
        return None
    candidates = (
        install_dir / "Bin" / "Sysbuilder.exe",
        install_dir / "Sysbuilder.exe",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve()


def get_sysml_v1_api_host() -> str:
    """返回内置 AI 指定的当前 SysML v1 ScriptService 主机。"""
    return (os.environ.get("SYSML_V1_API_HOST") or "127.0.0.1").strip()


def is_sysml_v1_embedded_mode() -> bool:
    """只要显式传入端口就进入固定实例模式，包括配置错误的端口。"""
    return bool((os.environ.get("SYSML_V1_API_PORT") or "").strip())


def get_sysml_v1_api_port() -> int | None:
    """返回内置 AI 指定的当前 SysML v1 ScriptService 端口。"""
    raw = (os.environ.get("SYSML_V1_API_PORT") or "").strip()
    if not raw:
        return None
    try:
        port = int(raw)
    except ValueError:
        return None
    return port if 1 <= port <= 65535 else None

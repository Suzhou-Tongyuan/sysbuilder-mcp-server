from __future__ import annotations

from pathlib import Path


_VERSION = "0.1.0"


def get_version_info() -> dict:
    return {
        "name": "sysbuilder_mcp",
        "version": _VERSION,
        "deploy_root": str(Path(__file__).resolve().parent),
        "project_root": str(Path(__file__).resolve().parent.parent),
    }


def format_version_banner() -> str:
    info = get_version_info()
    return f"{info['name']} {info['version']}"

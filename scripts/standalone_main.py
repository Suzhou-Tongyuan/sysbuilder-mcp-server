"""Sysbuilder MCP 单文件发行版入口。

该入口由 PyInstaller 打包，负责定位包内资源、包内 ``sysbuilder_mcp_server.core`` API，
以及 EXE 所在机器上的 Sysbuilder 主程序。运行时不依赖外置 Python 或 MCP 源码。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _source_project_root() -> Path:
    """返回源码树中的 MCP 运行包目录，供迁移后的构建入口自检使用。"""
    repository_root = Path(__file__).resolve().parent.parent
    return repository_root


def _bundle_root() -> Path:
    """返回单文件解包根目录；源码运行时退回 MCP 运行包目录。"""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root).resolve()
    return _source_project_root()


def _executable_directory() -> Path:
    """返回用户实际启动的 EXE 所在目录，用于发现外部 Sysbuilder 安装。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return _source_project_root()


def _find_sysbuilder_root(executable_directory: Path) -> Path | None:
    """发现 Sysbuilder 运行根目录，兼容标准 Tools、开发目录和独立复制场景。"""
    candidates: list[Path] = []
    if executable_directory.parent.name.casefold() == "tools":
        candidates.append(executable_directory.parent.parent)
    candidates.extend(list(executable_directory.parents)[:5])

    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        process_candidates = (
            resolved / "Release" / "Sysbuilder.exe",
            resolved / "Bin" / "Sysbuilder.exe",
            resolved / "Sysbuilder.exe",
        )
        if any(path.is_file() for path in process_candidates):
            return resolved
    return None


def _configure_frozen_environment() -> None:
    """配置单文件运行路径，并允许命令行参数在服务入口中继续覆盖默认值。"""
    bundle_root = _bundle_root()
    executable_directory = _executable_directory()
    os.environ.setdefault("MCP_DEPLOY_ROOT", str(bundle_root))

    resources_root = bundle_root / "resources"
    if resources_root.is_dir():
        os.environ.setdefault("MCP_RESOURCES_DIR", str(resources_root))

    runtime_root = _find_sysbuilder_root(executable_directory)
    if runtime_root is None:
        return
    os.environ.setdefault("SYSBUILDER_INSTALL_DIR", str(runtime_root))

    process_candidates = (
        runtime_root / "Release" / "Sysbuilder.exe",
        runtime_root / "Bin" / "Sysbuilder.exe",
        runtime_root / "Sysbuilder.exe",
    )
    for candidate in process_candidates:
        if candidate.is_file():
            os.environ.setdefault("SYSBUILDER_PROCESS_PATH", str(candidate.resolve()))
            break


def main() -> int:
    """启动内置 MCP 服务，适用于 PyInstaller 单文件和源码自检场景。"""
    _configure_frozen_environment()
    if not getattr(sys, "frozen", False):
        # 构建源码已与运行包分离，源码自检时需要显式加载运行包中的服务实现。
        sys.path.insert(0, str(_source_project_root()))
    from sysbuilder_mcp_server.main import main as run_server

    return run_server()


if __name__ == "__main__":
    raise SystemExit(main())

# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 单文件构建规格。"""
from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
    copy_metadata,
)


build_source_root = Path(SPECPATH).resolve()
repository_root = build_source_root.parent
project_root = repository_root
python_package_root = project_root / "sysbuilder_mcp_server"
mworks_api = python_package_root / "core" / "sysbuilder_api.py"
resources_root = project_root / "resources"

if not mworks_api.is_file():
    raise FileNotFoundError(f"缺少 Sysbuilder Python API: {mworks_api}")
if not python_package_root.is_dir():
    raise FileNotFoundError(f"缺少 MCP Python 包: {python_package_root}")
if not resources_root.is_dir():
    raise FileNotFoundError(f"缺少 MCP 资源目录: {resources_root}")

# FastMCP 包含通过字符串延迟加载的传输和协议模块；仅收集服务端路径，
# 避免把未使用且依赖可选 typer 的 mcp.cli 一并打入。
mcp_datas = collect_data_files("mcp")
mcp_binaries = collect_dynamic_libs("mcp")
mcp_hiddenimports = (
    collect_submodules("mcp.server", on_error="ignore")
    + collect_submodules("mcp.shared", on_error="ignore")
    + ["mcp.types"]
)
hiddenimports = sorted(
    set(
        mcp_hiddenimports
        + [
            "colorama",
            "jsonrpcclient",
            "packaging.version",
            "psutil",
            "websocket",
        ]
    )
)

datas = list(mcp_datas)
datas.extend(copy_metadata("mcp"))
datas.extend(
    [
        (str(resources_root), "resources"),
        # 第一份供本地 API 目录解析，第二份兼容 MwConnect 的冻结模式扫描。
        (str(mworks_api), "sysbuilder_mcp_server/core"),
        (str(mworks_api), "."),
    ]
)

a = Analysis(
    [str(build_source_root / "standalone_main.py")],
    pathex=[str(build_source_root), str(project_root)],
    binaries=mcp_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(build_source_root / "pyi_rth_sysbuilder_stdout.py")],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="sysbuilder-mcp-server-win64",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
)

"""定位并加载 Sysbuilder 软件自带的 ``mworks.sysbuilder`` API。"""
from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType


_API_RELATIVE_PATH = Path("mworks") / "sysbuilder" / "sysbuilder_api.py"


def _append_unique(items: list[Path], candidate: Path | None) -> None:
    """追加去重后的候选路径，避免同一路径被反复探测。"""
    if candidate is None:
        return
    try:
        resolved = candidate.expanduser().resolve()
    except OSError:
        return
    if resolved not in items:
        items.append(resolved)


def _candidate_site_packages() -> list[Path]:
    """按显式配置、运行目录和部署目录顺序生成 site-packages 候选。"""
    candidates: list[Path] = []
    explicit = (os.environ.get("SYSBUILDER_PYTHON_SITE_PACKAGES") or "").strip()
    if explicit:
        _append_unique(candidates, Path(explicit))

    roots: list[Path] = []
    install_dir = (
        os.environ.get("SYSML_V1_INSTALL_DIR")
        or os.environ.get("SYSBUILDER_INSTALL_DIR")
        or ""
    ).strip()
    if install_dir:
        install_path = Path(install_dir)
        _append_unique(roots, install_path)
        _append_unique(roots, install_path.parent)

    process_path = (os.environ.get("SYSBUILDER_PROCESS_PATH") or "").strip()
    if process_path:
        process_parent = Path(process_path).parent
        _append_unique(roots, process_parent)
        _append_unique(roots, process_parent.parent)

    deploy_root = Path(
        os.environ.get("MCP_DEPLOY_ROOT")
        or Path(__file__).resolve().parents[1]
    )
    _append_unique(roots, deploy_root)
    for parent in list(deploy_root.parents)[:4]:
        _append_unique(roots, parent)

    for root in roots:
        _append_unique(candidates, root / "external" / "Python311" / "Lib" / "site-packages")
    return candidates


def configure_external_api_path() -> Path:
    """将包含 ``mworks.sysbuilder`` 的软件内置 site-packages 放到导入路径首位。"""
    checked: list[str] = []
    for candidate in _candidate_site_packages():
        api_file = candidate / _API_RELATIVE_PATH
        checked.append(str(api_file))
        if not api_file.is_file():
            continue
        candidate_text = str(candidate)
        if candidate_text in sys.path:
            sys.path.remove(candidate_text)
        sys.path.insert(0, candidate_text)
        os.environ["SYSBUILDER_PYTHON_SITE_PACKAGES"] = candidate_text
        return candidate

    # 软件自带 Python 启动时，目标包通常已经位于 sys.path；保留这一兼容路径。
    try:
        spec = importlib.util.find_spec("mworks.sysbuilder.sysbuilder_api")
    except ModuleNotFoundError:
        spec = None
    if spec is not None and spec.origin:
        api_file = Path(spec.origin).resolve()
        site_packages = api_file.parents[2]
        os.environ.setdefault("SYSBUILDER_PYTHON_SITE_PACKAGES", str(site_packages))
        return site_packages

    detail = "\n  - ".join(checked) if checked else "（没有可探测路径）"
    raise ImportError(
        "未找到 Sysbuilder 自带的 mworks.sysbuilder API。已检查：\n  - " + detail
    )


def load_external_module(module_name: str) -> ModuleType:
    """加载指定的 ``mworks.sysbuilder`` 子模块，供 MCP core 兼容层复用。"""
    configure_external_api_path()
    return importlib.import_module(f"mworks.sysbuilder.{module_name}")


def get_external_api_source_path() -> Path:
    """返回实际使用的 sysbuilder_api.py，供 API 目录解析和查询工具读取。"""
    module = load_external_module("sysbuilder_api")
    module_file = getattr(module, "__file__", None)
    if not module_file:
        raise RuntimeError("mworks.sysbuilder.sysbuilder_api 没有可读取的源文件路径")
    return Path(module_file).resolve()


EXTERNAL_SITE_PACKAGES = configure_external_api_path()

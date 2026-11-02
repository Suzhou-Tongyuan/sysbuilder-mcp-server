"""保护 Windows stdio MCP 通道免受第三方注入诊断行污染。"""
from __future__ import annotations

import atexit
import os
import sys
import threading


def _is_rex_anomaly(line: bytes) -> bool:
    """识别 0patch/安全软件写入 stdout 的已知 REX 诊断噪声。"""
    stripped = line.strip()
    return (
        stripped.startswith(b"[0x")
        and b"] ANOMALY:" in stripped
        and b"REX" in stripped
    )


def _install_native_stdout_filter() -> None:
    """代理 fd 1 并过滤原生噪声，保证传给 MCP 客户端的每行都是有效协议输出。"""
    if os.name != "nt":
        return

    import ctypes
    import msvcrt
    from ctypes import wintypes

    try:
        stdout_fd = sys.stdout.fileno()
    except (AttributeError, OSError, ValueError):
        return

    stdout_handle_id = -11
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.SetStdHandle.argtypes = [wintypes.DWORD, wintypes.HANDLE]
    kernel32.SetStdHandle.restype = wintypes.BOOL

    saved_stdout_fd = os.dup(stdout_fd)
    read_fd, write_fd = os.pipe()
    os.set_inheritable(read_fd, False)
    os.set_inheritable(write_fd, False)
    try:
        sys.stdout.flush()
        os.dup2(write_fd, stdout_fd)
        os.close(write_fd)
        write_fd = -1
        redirected_handle = wintypes.HANDLE(msvcrt.get_osfhandle(stdout_fd))
        if not kernel32.SetStdHandle(stdout_handle_id, redirected_handle):
            raise OSError(ctypes.get_last_error(), "SetStdHandle failed")
    except OSError:
        os.dup2(saved_stdout_fd, stdout_fd)
        os.close(saved_stdout_fd)
        os.close(read_fd)
        if write_fd >= 0:
            os.close(write_fd)
        return

    def forward(line: bytes) -> None:
        """把非噪声输出写回 MCP 客户端持有的原始 stdout 管道。"""
        if not _is_rex_anomaly(line):
            os.write(saved_stdout_fd, line)

    def pump() -> None:
        """持续按行代理 stdout，兼容 JSON-RPC 分块写入和无换行尾数据。"""
        pending = b""
        try:
            with os.fdopen(read_fd, "rb", buffering=0) as reader:
                while True:
                    chunk = reader.read(4096)
                    if not chunk:
                        break
                    pending += chunk
                    while b"\n" in pending:
                        line, pending = pending.split(b"\n", 1)
                        forward(line + b"\n")
                if pending:
                    forward(pending)
        except (BrokenPipeError, OSError, ValueError):
            # 客户端关闭管道或进程退出时不再制造新的 stderr 噪声。
            return

    thread = threading.Thread(target=pump, name="native-stdout-filter", daemon=True)
    thread.start()

    def close_filter() -> None:
        """刷新协议输出、恢复 fd 1，并等待过滤线程转发剩余完整行。"""
        try:
            sys.stdout.flush()
        except (BrokenPipeError, OSError, ValueError):
            pass
        try:
            os.dup2(saved_stdout_fd, stdout_fd)
            restored_handle = wintypes.HANDLE(msvcrt.get_osfhandle(stdout_fd))
            kernel32.SetStdHandle(stdout_handle_id, restored_handle)
        except OSError:
            pass
        thread.join(timeout=1.0)
        try:
            os.close(saved_stdout_fd)
        except OSError:
            pass

    atexit.register(close_filter)


_install_native_stdout_filter()

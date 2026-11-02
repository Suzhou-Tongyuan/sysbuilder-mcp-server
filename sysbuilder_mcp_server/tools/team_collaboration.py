"""Sysbuilder 团队协同 MCP 工具。"""
from __future__ import annotations
import json

from typing import Any

from sysbuilder_mcp_server.core import sysbuilder_api
from sysbuilder_mcp_server.core.sysbuilder_connect import MwConnect

from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.tools.common import (
    _json,
    capture_python_output,
    ensure_sysbuilder_session,
)


def _active_session() -> dict[str, Any]:
    """读取当前脚本连接状态，适用于不能隐式启动软件的退出场景。"""
    connected = MwConnect().get_is_connected()
    return {
        "ok": connected,
        "action": "already_connected" if connected else "not_connected",
        "stdout": "",
        "stderr": "",
    }
def _redact_sensitive_text(text: str, sensitive_values: list[str]) -> str:
    """清理 API 输出中的敏感值，适用于登录密码等禁止回显的数据。"""
    redacted = text
    for sensitive_value in sensitive_values:
        if sensitive_value:
            redacted = redacted.replace(sensitive_value, "***")
    return redacted




def _invoke_team_api(
    tool_name: str,
    api_name: str,
    *args: Any,
    start_if_needed: bool = True,
) -> str:
    """统一建立会话、调用团队 API 并返回可诊断的结构化结果。"""
    api_func = getattr(sysbuilder_api, api_name, None)
    if not callable(api_func):
        return _json(
            {
                "ok": False,
                "tool": tool_name,
                "api": api_name,
                "error": (
                    f"当前 Sysbuilder Python API 不支持 {api_name}；"
                    "请确认软件版本包含团队协同 API。"
                ),
            }
        )

    session = ensure_sysbuilder_session() if start_if_needed else _active_session()
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": tool_name,
                "api": api_name,
                "error": "未连接到 Sysbuilder。",
                "session": session,
            }
        )

    sensitive_values = []
    if api_name == "LoginTeam" and len(args) >= 3:
        # 登录密码不得通过底层异常、标准输出或错误输出回流到 MCP 客户端。
        sensitive_values.append(str(args[2]))

    try:
        with capture_python_output() as (buf_out, buf_err):
            result = api_func(*args)
    except Exception as exc:
        return _json(
            {
                "ok": False,
                "tool": tool_name,
                "api": api_name,
                "error": _redact_sensitive_text(str(exc), sensitive_values),
                "session": session,
            }
        )

    # 查询接口允许合法地返回空字典或空列表；布尔接口则以返回值表示业务结果。
    ok = bool(result) if isinstance(result, bool) else result is not None
    return _json(
        {
            "ok": ok,
            "tool": tool_name,
            "api": api_name,
            "result": result,
            "error": "" if ok else f"{api_name} 返回失败。",
            "session": session,
            "stdout": _redact_sensitive_text(buf_out.getvalue(), sensitive_values),
            "stderr": _redact_sensitive_text(buf_err.getvalue(), sensitive_values),
        }
    )


def _invalid(tool_name: str, error: str, **details: Any) -> str:
    """返回输入校验失败结果，适用于调用软件 API 之前的快速失败。"""
    return _json({"ok": False, "tool": tool_name, "error": error, **details})


def _confirmed(tool_name: str, confirm: bool, operation: str) -> str | None:
    """保护不可逆操作，仅在用户明确确认后允许继续执行。"""
    if confirm:
        return None
    return _invalid(
        tool_name,
        f"{operation}可能丢失数据或删除远程资源，必须在用户明确确认后传入 confirm=true。",
        requires_confirmation=True,
    )


def _normalize_files(files: list[str] | None) -> tuple[list[str], str]:
    """规范化仓库相对路径列表，并拒绝非字符串或空路径。"""
    if not files:
        return [], ""

    normalized: list[str] = []
    for file_path in files:
        if not isinstance(file_path, str) or not file_path.strip():
            return [], "files 只能包含非空的仓库相对路径字符串。"
        clean_path = file_path.strip()
        if clean_path not in normalized:
            normalized.append(clean_path)
    return normalized, ""
def _normalize_action(action: str) -> str:
    """规范化领域工具动作名，兼容连字符与大小写差异。"""
    return (action or "").strip().lower().replace("-", "_")


def _dispatch_result(raw_result: str, tool_name: str, action: str) -> str:
    """把内部 API 包装结果转换为领域工具统一返回结构。"""
    payload = json.loads(raw_result)
    operation = payload.get("tool")
    if operation and operation != tool_name:
        payload["operation"] = operation
    payload["tool"] = tool_name
    payload["action"] = action
    return _json(payload)




def login_team(server_address: str, user_name: str, password: str) -> str:
    """登录团队资源服务器；适用于后续访问分类、仓库和协同工程。"""
    tool_name = "login_team"
    server = (server_address or "").strip()
    user = (user_name or "").strip()
    if not server or not user or not password:
        return _invalid(tool_name, "server_address、user_name 和 password 均不能为空。")

    # 密码只传给底层 API，不写入 MCP 返回值或日志字段。
    return _invoke_team_api(tool_name, "LoginTeam", server, user, password)


def logout_team() -> str:
    """退出当前团队账号；不会退出 Sysbuilder，也不会为退出操作隐式启动软件。"""
    return _invoke_team_api("logout_team", "LogoutTeam", start_if_needed=False)


def get_team_session_info() -> str:
    """查询团队登录状态、服务器地址、用户名和本地仓库根目录。"""
    return _invoke_team_api("get_team_session_info", "GetTeamSessionInfo")


def list_team_resources() -> str:
    """递归列出“我的仓库”中的团队分类和仓库资源树。"""
    return _invoke_team_api("list_team_resources", "ListTeamResources")


def search_public_team_repositories(keyword: str = "") -> str:
    """按名称关键字搜索公共团队仓库；空关键字表示查询全部可见仓库。"""
    return _invoke_team_api(
        "search_public_team_repositories",
        "SearchPublicTeamRepositories",
        (keyword or "").strip(),
    )


def list_local_team_repositories() -> str:
    """列出本机团队仓库根目录中的有效 Git 仓库和工程文件。"""
    return _invoke_team_api("list_local_team_repositories", "ListLocalTeamRepositories")


def create_team_group(parent_group_path: str, name: str, description: str = "") -> str:
    """在指定团队分类下创建子分类；父路径为空时创建顶层分类。"""
    tool_name = "create_team_group"
    group_name = (name or "").strip()
    if not group_name:
        return _invalid(tool_name, "name 不能为空。")
    return _invoke_team_api(
        tool_name,
        "CreateTeamGroup",
        (parent_group_path or "").strip(),
        group_name,
        (description or "").strip(),
    )


def update_team_group(target_group_path: str, new_name: str, new_description: str = "") -> str:
    """修改指定远程团队分类的名称和描述。"""
    tool_name = "update_team_group"
    group_path = (target_group_path or "").strip()
    group_name = (new_name or "").strip()
    if not group_path or not group_name:
        return _invalid(tool_name, "target_group_path 和 new_name 均不能为空。")
    return _invoke_team_api(
        tool_name,
        "UpdateTeamGroup",
        group_path,
        group_name,
        (new_description or "").strip(),
    )


def delete_team_group(group_path: str, confirm: bool = False) -> str:
    """删除远程团队分类；仅在用户明确确认后传入 ``confirm=true``。"""
    tool_name = "delete_team_group"
    confirmation_error = _confirmed(tool_name, confirm, "删除团队分类")
    if confirmation_error:
        return confirmation_error
    target = (group_path or "").strip()
    if not target:
        return _invalid(tool_name, "group_path 不能为空。")
    return _invoke_team_api(tool_name, "DeleteTeamGroup", target)


def create_team_repository(group_path: str, name: str, description: str = "") -> str:
    """在指定远程分类下创建空团队仓库；发布已有工程请使用发布工具。"""
    tool_name = "create_team_repository"
    target = (group_path or "").strip()
    repository_name = (name or "").strip()
    if not target or not repository_name:
        return _invalid(tool_name, "group_path 和 name 均不能为空。")
    return _invoke_team_api(
        tool_name,
        "CreateTeamRepository",
        target,
        repository_name,
        (description or "").strip(),
    )


def clone_team_repository(resource_path: str) -> str:
    """按远程可见路径克隆单个团队仓库到本地团队仓库根目录。"""
    tool_name = "clone_team_repository"
    target = (resource_path or "").strip()
    if not target:
        return _invalid(tool_name, "resource_path 不能为空。")
    return _invoke_team_api(tool_name, "CloneTeamRepository", target)


def clone_team_group(group_path: str) -> str:
    """递归克隆指定团队分类中的全部仓库，适用于批量获取协同工程。"""
    tool_name = "clone_team_group"
    target = (group_path or "").strip()
    if not target:
        return _invalid(tool_name, "group_path 不能为空。")
    return _invoke_team_api(tool_name, "CloneTeamGroup", target)


def publish_project_to_team(
    target_group_path: str,
    repository_name: str,
    description: str = "",
) -> str:
    """把当前打开的本地工程发布为指定分类下的团队仓库。"""
    tool_name = "publish_project_to_team"
    target = (target_group_path or "").strip()
    name = (repository_name or "").strip()
    if not target or not name:
        return _invalid(tool_name, "target_group_path 和 repository_name 均不能为空。")
    return _invoke_team_api(
        tool_name,
        "PublishProjectToTeam",
        target,
        name,
        (description or "").strip(),
    )


def get_team_repository_status() -> str:
    """查询当前打开团队工程的分支、修改、未跟踪文件和冲突状态。"""
    return _invoke_team_api("get_team_repository_status", "GetTeamRepositoryStatus")


def commit_team_repository(message: str, files: list[str] | None = None) -> str:
    """提交当前团队工程；文件列表为空时提交全部本地变更。"""
    tool_name = "commit_team_repository"
    commit_message = (message or "").strip()
    if not commit_message:
        return _invalid(tool_name, "message 不能为空。")
    normalized_files, error = _normalize_files(files)
    if error:
        return _invalid(tool_name, error)
    return _invoke_team_api(
        tool_name,
        "CommitTeamRepository",
        commit_message,
        normalized_files,
    )


def pull_team_repository() -> str:
    """拉取并合并当前团队工程的远程更新；调用前应先检查冲突和本地状态。"""
    return _invoke_team_api("pull_team_repository", "PullTeamRepository")


def push_team_repository() -> str:
    """把当前团队工程中已经提交的本地提交推送到远程仓库。"""
    return _invoke_team_api("push_team_repository", "PushTeamRepository")


def get_team_repository_history() -> str:
    """获取当前团队工程最近的非合并提交历史，最多返回 200 条。"""
    return _invoke_team_api("get_team_repository_history", "GetTeamRepositoryHistory")


def get_team_commit_details(commit_id: str) -> str:
    """查询当前团队工程中指定提交的作者、时间、说明和文件变更。"""
    tool_name = "get_team_commit_details"
    target = (commit_id or "").strip()
    if not target:
        return _invalid(tool_name, "commit_id 不能为空。")
    return _invoke_team_api(tool_name, "GetTeamCommitDetails", target)


def restore_team_repository_files(
    files: list[str] | None = None,
    confirm: bool = False,
) -> str:
    """丢弃指定文件的未提交变更；文件列表为空时还原全部，需明确确认。"""
    tool_name = "restore_team_repository_files"
    confirmation_error = _confirmed(tool_name, confirm, "还原团队仓库文件")
    if confirmation_error:
        return confirmation_error
    normalized_files, error = _normalize_files(files)
    if error:
        return _invalid(tool_name, error)
    return _invoke_team_api(tool_name, "RestoreTeamRepositoryFiles", normalized_files)


def reset_team_repository_version(commit_id: str, confirm: bool = False) -> str:
    """把当前团队工程重置到指定提交；此操作可能丢失本地状态，需明确确认。"""
    tool_name = "reset_team_repository_version"
    confirmation_error = _confirmed(tool_name, confirm, "重置团队仓库版本")
    if confirmation_error:
        return confirmation_error
    target = (commit_id or "").strip()
    if not target:
        return _invalid(tool_name, "commit_id 不能为空。")
    return _invoke_team_api(tool_name, "ResetTeamRepositoryVersion", target)
_SESSION_ACTIONS = ("login", "logout", "info")
_RESOURCE_ACTIONS = (
    "list_remote",
    "search_public",
    "list_local",
    "create_group",
    "update_group",
    "delete_group",
    "create_repository",
    "clone_repository",
    "clone_group",
    "publish_project",
)
_REPOSITORY_ACTIONS = ("status", "commit", "pull", "push")
_HISTORY_ACTIONS = ("list", "details", "restore_files", "reset_version")


@mcp.tool()
def team_session(
    action: str,
    server_address: str = "",
    user_name: str = "",
    password: str = "",
) -> str:
    """管理团队会话。

    action 支持 login、logout、info。仅 login 使用 server_address、user_name 和
    password；密码只传给底层登录 API，并在输出和异常中脱敏。
    """
    normalized_action = _normalize_action(action)
    if normalized_action == "login":
        result = login_team(server_address, user_name, password)
    elif normalized_action == "logout":
        result = logout_team()
    elif normalized_action == "info":
        result = get_team_session_info()
    else:
        return _invalid(
            "team_session",
            "不支持的 action。",
            action=normalized_action,
            allowed_actions=list(_SESSION_ACTIONS),
        )
    return _dispatch_result(result, "team_session", normalized_action)


@mcp.tool()
def team_resources(
    action: str,
    path: str = "",
    name: str = "",
    description: str = "",
    keyword: str = "",
    confirm: bool = False,
) -> str:
    """查询或管理团队资源。

    action 支持 list_remote、search_public、list_local、create_group、
    update_group、delete_group、create_repository、clone_repository、
    clone_group、publish_project。path 统一表示相应操作的分类或仓库可见路径；
    name 表示新分类名、仓库名或发布后的仓库名。
    """
    normalized_action = _normalize_action(action)
    if normalized_action == "list_remote":
        result = list_team_resources()
    elif normalized_action == "search_public":
        result = search_public_team_repositories(keyword)
    elif normalized_action == "list_local":
        result = list_local_team_repositories()
    elif normalized_action == "create_group":
        result = create_team_group(path, name, description)
    elif normalized_action == "update_group":
        result = update_team_group(path, name, description)
    elif normalized_action == "delete_group":
        result = delete_team_group(path, confirm)
    elif normalized_action == "create_repository":
        result = create_team_repository(path, name, description)
    elif normalized_action == "clone_repository":
        result = clone_team_repository(path)
    elif normalized_action == "clone_group":
        result = clone_team_group(path)
    elif normalized_action == "publish_project":
        result = publish_project_to_team(path, name, description)
    else:
        return _invalid(
            "team_resources",
            "不支持的 action。",
            action=normalized_action,
            allowed_actions=list(_RESOURCE_ACTIONS),
        )
    return _dispatch_result(result, "team_resources", normalized_action)


@mcp.tool()
def team_repository(
    action: str,
    message: str = "",
    files: list[str] | None = None,
) -> str:
    """操作当前打开团队工程的仓库。

    action 支持 status、commit、pull、push。仅 commit 使用 message 和 files；
    files 为空时提交全部变更。提交、拉取或推送前应先执行 status。
    """
    normalized_action = _normalize_action(action)
    if normalized_action == "status":
        result = get_team_repository_status()
    elif normalized_action == "commit":
        result = commit_team_repository(message, files)
    elif normalized_action == "pull":
        result = pull_team_repository()
    elif normalized_action == "push":
        result = push_team_repository()
    else:
        return _invalid(
            "team_repository",
            "不支持的 action。",
            action=normalized_action,
            allowed_actions=list(_REPOSITORY_ACTIONS),
        )
    return _dispatch_result(result, "team_repository", normalized_action)


@mcp.tool()
def team_history(
    action: str,
    commit_id: str = "",
    files: list[str] | None = None,
    confirm: bool = False,
) -> str:
    """查询历史或执行版本恢复操作。

    action 支持 list、details、restore_files、reset_version。details 和
    reset_version 使用 commit_id，restore_files 使用 files；还原或重置必须在
    用户明确确认后传入 confirm=true。
    """
    normalized_action = _normalize_action(action)
    if normalized_action == "list":
        result = get_team_repository_history()
    elif normalized_action == "details":
        result = get_team_commit_details(commit_id)
    elif normalized_action == "restore_files":
        result = restore_team_repository_files(files, confirm)
    elif normalized_action == "reset_version":
        result = reset_team_repository_version(commit_id, confirm)
    else:
        return _invalid(
            "team_history",
            "不支持的 action。",
            action=normalized_action,
            allowed_actions=list(_HISTORY_ACTIONS),
        )
    return _dispatch_result(result, "team_history", normalized_action)

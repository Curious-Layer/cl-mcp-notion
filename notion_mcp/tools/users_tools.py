"""Users group: list_users, get_user, get_self"""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas import (
    BotUserData,
    GetSelfResult,
    GetUserResult,
    ListUsersData,
    ListUsersResult,
    UserData,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("notion-mcp.tools.users")


def register_users_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_users",
        description="List all users in the workspace (guests not included)",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_users(
        page_size: int = Field(default=100, description="Maximum number of users to return per page (values above 100 are clamped)."),
        start_cursor: str | None = Field(default=None, description="Cursor from a previous response's next_cursor, used to page through results."),
    ) -> ListUsersResult:
        tlog = ToolLogger(logger, "list_users")
        try:
            params: dict = {"page_size": min(page_size, 100)}
            if start_cursor:
                params["start_cursor"] = start_cursor

            data, status, retry_after = service.notion_request("GET", "/v1/users", params=params)
            if 200 <= status < 300:
                tlog.success()
                return ListUsersResult(
                    success=True,
                    statusCode=status,
                    data=ListUsersData(
                        results=[UserData(**u) for u in data.get("results", [])],
                        has_more=data.get("has_more", False),
                        next_cursor=data.get("next_cursor"),
                    ),
                )
            return _upstream_err(ListUsersResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(ListUsersResult, tlog, exc)

    @mcp.tool(
        name="get_user",
        description="Retrieve a specific user by their ID",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_user(
        user_id: str = Field(description="ID of the user to retrieve."),
    ) -> GetUserResult:
        tlog = ToolLogger(logger, "get_user")
        try:
            data, status, retry_after = service.notion_request("GET", f"/v1/users/{user_id}")
            if 200 <= status < 300:
                tlog.success()
                return GetUserResult(success=True, statusCode=status, data=UserData(**data))
            return _upstream_err(GetUserResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetUserResult, tlog, exc)

    @mcp.tool(
        name="get_self",
        description="Retrieve the bot user associated with your API token, including owner and workspace info",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_self() -> GetSelfResult:
        tlog = ToolLogger(logger, "get_self")
        try:
            data, status, retry_after = service.notion_request("GET", "/v1/users/me")
            if 200 <= status < 300:
                tlog.success()
                bot = data.get("bot", {}) or {}
                return GetSelfResult(
                    success=True,
                    statusCode=status,
                    data=BotUserData(
                        **data,
                        owner=bot.get("owner"),
                        workspace_name=bot.get("workspace_name"),
                        workspace_limits=bot.get("workspace_limits"),
                    ),
                )
            return _upstream_err(GetSelfResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetSelfResult, tlog, exc)

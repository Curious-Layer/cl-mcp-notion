"""Pydantic output schemas for MewCP Notion MCP Server."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Base envelope — shared across all tools
# ---------------------------------------------------------------------------

class ToolError(BaseModel):
    code: str
    message: str
    details: Any = None


class ToolResult(BaseModel):
    success: bool
    statusCode: int
    retriable: bool = False
    retry_after_seconds: int | None = None
    error: ToolError | None = None


# ---------------------------------------------------------------------------
# Page models
# ---------------------------------------------------------------------------

class PageData(BaseModel):
    """Raw Notion page object — used by get_page, create_page_under_page,
    create_workspace_page, and as the before/after member of update_page."""
    model_config = ConfigDict(extra="allow")

    id: str | None
    object: str | None
    url: str | None
    public_url: str | None = None
    created_time: str | None
    last_edited_time: str | None
    archived: bool | None = None
    in_trash: bool | None = None
    parent: dict | None = None
    properties: dict | None = None
    icon: dict | None = None
    cover: dict | None = None


class GetPageResult(ToolResult):
    data: PageData | None = None


class CreatePageUnderPageData(PageData):
    """Newly created page under a parent page — same shape as PageData."""


class CreatePageUnderPageResult(ToolResult):
    data: CreatePageUnderPageData | None = None


class CreateWorkspacePageData(PageData):
    """Newly created top-level workspace page — same shape as PageData."""


class CreateWorkspacePageResult(ToolResult):
    data: CreateWorkspacePageData | None = None


class UpdatePageData(BaseModel):
    """Updated page — before/after state per the MewCP audit rule requiring
    UPDATE tools to return both."""
    model_config = ConfigDict(extra="allow")

    before: PageData
    after: PageData


class UpdatePageResult(ToolResult):
    data: UpdatePageData | None = None


# ---------------------------------------------------------------------------
# Search models
# ---------------------------------------------------------------------------

class SearchResultItem(BaseModel):
    """Simplified search hit — title extracted from properties.title array,
    same simplification the legacy search_notion_service already applied."""
    model_config = ConfigDict(extra="allow")

    id: str | None
    title: str
    url: str | None
    last_edited_time: str | None


class SearchNotionData(BaseModel):
    model_config = ConfigDict(extra="allow")

    pages: list[SearchResultItem] = []
    has_more: bool = False
    next_cursor: str | None = None


class SearchNotionResult(ToolResult):
    data: SearchNotionData | None = None


# ---------------------------------------------------------------------------
# Fetch page content model
# ---------------------------------------------------------------------------

class FetchPageContentData(BaseModel):
    """Simplified page content — title + flattened plain text of its blocks.
    Carries has_more_children/next_cursor/children_count through so pagination
    info computed by the tool isn't silently dropped (a bug in the legacy
    _simplify_page_response, which computed these fields but never returned them)."""
    model_config = ConfigDict(extra="allow")

    page_id: str | None
    title: str
    content: str
    url: str | None
    has_more_children: bool | None = None
    next_cursor: str | None = None
    children_count: int | None = None


class FetchPageContentResult(ToolResult):
    data: FetchPageContentData | None = None


# ---------------------------------------------------------------------------
# Database models
# ---------------------------------------------------------------------------

class DatabaseData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None
    title: list | None = None
    parent: dict | None = None
    data_sources: list | None = None
    url: str | None = None
    archived: bool | None = None
    created_time: str | None = None
    last_edited_time: str | None = None
    icon: dict | None = None
    cover: dict | None = None


class GetDatabaseResult(ToolResult):
    data: DatabaseData | None = None


class CreateDatabaseData(DatabaseData):
    """Newly created database — same shape as DatabaseData."""


class CreateDatabaseResult(ToolResult):
    data: CreateDatabaseData | None = None


# ---------------------------------------------------------------------------
# Data source models
# ---------------------------------------------------------------------------

class DataSourceData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None
    properties: dict | None = None
    parent: dict | None = None


class GetDataSourceResult(ToolResult):
    data: DataSourceData | None = None


class QueryDataSourceData(BaseModel):
    """results kept as raw dicts — each database's `properties` shape varies
    per-schema, so keep as raw dict rather than over-modeling."""
    model_config = ConfigDict(extra="allow")

    results: list[dict] = []
    has_more: bool = False
    next_cursor: str | None = None


class QueryDataSourceResult(ToolResult):
    data: QueryDataSourceData | None = None


# ---------------------------------------------------------------------------
# User models
# ---------------------------------------------------------------------------

class UserData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None
    name: str | None = None
    avatar_url: str | None = None
    type: str | None = None
    person: dict | None = None
    bot: dict | None = None


class ListUsersData(BaseModel):
    model_config = ConfigDict(extra="allow")

    results: list[UserData] = []
    has_more: bool = False
    next_cursor: str | None = None


class ListUsersResult(ToolResult):
    data: ListUsersData | None = None


class GetUserResult(ToolResult):
    data: UserData | None = None


class BotUserData(UserData):
    """/v1/users/me response. owner/workspace_name/workspace_limits live
    nested inside the raw response's `bot` dict (e.g. bot.workspace_name, per
    the legacy get_self_service code) but are promoted to top-level fields
    here since callers want them directly."""

    owner: dict | None = None
    workspace_name: str | None = None
    workspace_limits: dict | None = None


class GetSelfResult(ToolResult):
    data: BotUserData | None = None


# ---------------------------------------------------------------------------
# Block models
# ---------------------------------------------------------------------------

class BlockData(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    type: str | None = None
    created_time: str | None = None


class AppendTextBlockData(BaseModel):
    model_config = ConfigDict(extra="allow")

    blocks: list[BlockData] = []


class AppendTextBlockResult(ToolResult):
    data: AppendTextBlockData | None = None

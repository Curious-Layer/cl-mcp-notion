"""Databases group: get_database, get_data_source, query_data_source, create_database."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas import (
    CreateDatabaseData,
    CreateDatabaseResult,
    DatabaseData,
    DataSourceData,
    GetDatabaseResult,
    GetDataSourceResult,
    QueryDataSourceData,
    QueryDataSourceResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("notion-mcp.tools.databases")


def register_databases_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_database",
        description="Retrieve a database object by ID with title, parent, and data sources",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_database(
        database_id: str = Field(description="The ID of the database to retrieve"),
    ) -> GetDatabaseResult:
        tlog = ToolLogger(logger, "get_database")
        try:
            data, status, retry_after = service.notion_request(
                "GET", f"/v1/databases/{database_id}"
            )
            if 200 <= status < 300:
                tlog.success()
                return GetDatabaseResult(success=True, statusCode=status, data=DatabaseData(**data))
            return _upstream_err(GetDatabaseResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetDatabaseResult, tlog, exc)

    @mcp.tool(
        name="get_data_source",
        description="Retrieve a data source (database schema/properties) by ID",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_data_source(
        data_source_id: str = Field(description="The ID of the data source to retrieve"),
    ) -> GetDataSourceResult:
        tlog = ToolLogger(logger, "get_data_source")
        try:
            data, status, retry_after = service.notion_request(
                "GET", f"/v1/data_sources/{data_source_id}"
            )
            if 200 <= status < 300:
                tlog.success()
                return GetDataSourceResult(success=True, statusCode=status, data=DataSourceData(**data))
            return _upstream_err(GetDataSourceResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetDataSourceResult, tlog, exc)

    @mcp.tool(
        name="query_data_source",
        description="Query a data source to get pages with optional filtering and sorting",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def query_data_source(
        data_source_id: str = Field(description="The ID of the data source to query"),
        filter: dict | None = Field(
            default=None, description="Notion filter object to restrict which pages are returned"
        ),
        sorts: list | None = Field(
            default=None, description="List of Notion sort objects controlling result order"
        ),
        page_size: int = Field(
            default=100, description="Maximum number of results per page (silently capped at 100)"
        ),
        start_cursor: str | None = Field(
            default=None, description="Cursor from a previous response's next_cursor to page through results"
        ),
    ) -> QueryDataSourceResult:
        tlog = ToolLogger(logger, "query_data_source")
        try:
            body = {"page_size": min(page_size, 100)}

            if filter:
                body["filter"] = filter

            if sorts:
                body["sorts"] = sorts

            if start_cursor:
                body["start_cursor"] = start_cursor

            data, status, retry_after = service.notion_request(
                "POST", f"/v1/data_sources/{data_source_id}/query", body=body
            )
            if 200 <= status < 300:
                tlog.success()
                return QueryDataSourceResult(
                    success=True,
                    statusCode=status,
                    data=QueryDataSourceData(
                        results=data.get("results", []),
                        has_more=data.get("has_more", False),
                        next_cursor=data.get("next_cursor"),
                    ),
                )
            return _upstream_err(QueryDataSourceResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(QueryDataSourceResult, tlog, exc)

    @mcp.tool(
        name="create_database",
        description="Create a new database as a child of an existing page",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_database(
        parent_id: str = Field(description="The ID of the parent page to create the database under"),
        title: str = Field(default="Untitled Database", description="Title of the new database"),
        description: str | None = Field(
            default=None, description="Plain-text description of the database"
        ),
        properties: dict | None = Field(
            default=None,
            description="Database schema properties keyed by column name (defaults to a single 'Name' title property)",
        ),
        is_inline: bool = Field(
            default=False, description="Whether the database should render inline within its parent page"
        ),
        icon: dict | None = Field(default=None, description="Icon object to set on the database"),
        cover: dict | None = Field(default=None, description="Cover object to set on the database"),
    ) -> CreateDatabaseResult:
        tlog = ToolLogger(logger, "create_database")
        try:
            if not properties:
                properties = {"Name": {"title": {}}}

            # converting List to rich text format as per API spec
            title_rich_text = [{"type": "text", "text": {"content": title}}]

            body = {
                "parent": {"type": "page_id", "page_id": parent_id},
                "title": title_rich_text,
                "initial_data_source": {"properties": properties},
                "is_inline": is_inline,
            }

            # converting string description to rich text format as per API spec
            if description is not None:
                body["description"] = [{"type": "text", "text": {"content": description}}]

            if icon is not None:
                body["icon"] = icon

            if cover is not None:
                body["cover"] = cover

            data, status, retry_after = service.notion_request("POST", "/v1/databases", body=body)
            if 200 <= status < 300:
                tlog.success()
                return CreateDatabaseResult(success=True, statusCode=status, data=CreateDatabaseData(**data))
            return _upstream_err(CreateDatabaseResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CreateDatabaseResult, tlog, exc)

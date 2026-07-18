"""Pages read group: search_notion, get_page, fetch_page_content."""

import logging
from typing import Literal

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..config import CONNECT_TIMEOUT, READ_TIMEOUT
from ..logging_utils import ToolLogger
from ..schemas import (
    FetchPageContentData,
    FetchPageContentResult,
    GetPageResult,
    PageData,
    SearchNotionData,
    SearchNotionResult,
    SearchResultItem,
)
from ._helpers import _handle_request_exc, _upstream_err

logger = logging.getLogger("notion-mcp.tools.pages_read")


# ---------------------------------------------------------------------------
# Module-level helpers for fetch_page_content — pure logic, not tools, so
# they don't need `mcp` in scope. Ported from the legacy
# tools/read_operations.py implementations, swapped over to
# service.notion_request(...) and checked by status code instead of the
# legacy `"error" in result` dict-shape check.
# ---------------------------------------------------------------------------

def _fetch_block_children_recursive(
    block_id: str, max_depth: int = 3, current_depth: int = 0
) -> list:
    if current_depth >= max_depth:
        logger.warning(
            "Max recursion depth (%d) reached for block %s", max_depth, block_id
        )
        return []

    all_blocks: list = []
    start_cursor = None

    while True:
        params = {"page_size": 100}
        if start_cursor:
            params["start_cursor"] = start_cursor

        data, status, _ = service.notion_request(
            "GET",
            f"/v1/blocks/{block_id}/children",
            params=params,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
        )

        if not (200 <= status < 300):
            logger.error(
                "Failed to fetch children for block %s: HTTP %s", block_id, status
            )
            break

        blocks = data.get("results", [])

        for block in blocks:
            if block.get("has_children", False):
                block_type = block.get("type")
                logger.info(
                    "Fetching nested children for %s block %s",
                    block_type,
                    block["id"],
                )
                nested_children = _fetch_block_children_recursive(
                    block["id"], max_depth, current_depth + 1
                )
                block["children"] = nested_children

        all_blocks.extend(blocks)

        if not data.get("has_more", False):
            break

        start_cursor = data.get("next_cursor")

    return all_blocks


def _extract_title(page_data: dict) -> str:
    """Extract the title from page properties."""
    try:
        title_property = page_data.get("properties", {}).get("title", {})
        title_items = title_property.get("title", [])

        if title_items:
            return "".join(item.get("plain_text", "") for item in title_items)
        return ""
    except Exception:
        return ""


def _extract_plain_text(blocks: list) -> str:
    """Extract plain text content from Notion blocks recursively."""
    text_parts = []

    for block in blocks:
        block_type = block.get("type")

        if not block_type:
            continue

        block_content = block.get(block_type, {})
        rich_text = block_content.get("rich_text", [])

        for text_item in rich_text:
            plain_text = text_item.get("plain_text", "")
            if plain_text:
                text_parts.append(plain_text)

        if block.get("has_children"):
            # already-loaded children only
            children = block.get("children", [])
            if children:
                child_text = _extract_plain_text(children)
                if child_text:
                    text_parts.append(child_text)

    return "\n".join(text_parts)


def register_pages_read_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="search_notion",
        description="Search all pages and databases by title or list all pages  ",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def search_notion(
        query: str = Field(
            default="", description="Search query string, keep it empty to list all pages"
        ),
        filter_type: Literal["page", "data_source"] | None = Field(
            default=None, description="Filter by 'page' or 'data_source'. "
        ),
        page_size: int = Field(
            default=20, description="Number of pages to return (max 100)"
        ),
        start_cursor: str | None = Field(
            default=None,
            description="Cursor from a previous response to page through results.",
        ),
    ) -> SearchNotionResult:
        tlog = ToolLogger(logger, "search_notion")
        try:
            body: dict = {"query": query, "page_size": min(page_size, 100)}
            if filter_type is not None:
                body["filter"] = {"property": "object", "value": filter_type}
            if start_cursor:
                body["start_cursor"] = start_cursor

            data, status, retry_after = service.notion_request(
                "POST",
                "/v1/search",
                body=body,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                pages = []
                for item in data.get("results", []):
                    title_array = (
                        item.get("properties", {}).get("title", {}).get("title", [])
                    )
                    title = title_array[0].get("plain_text", "") if title_array else ""
                    pages.append(
                        SearchResultItem(
                            id=item.get("id"),
                            title=title.strip(),
                            url=item.get("url"),
                            last_edited_time=item.get("last_edited_time"),
                        )
                    )

                tlog.success()
                return SearchNotionResult(
                    success=True,
                    statusCode=status,
                    data=SearchNotionData(
                        pages=pages,
                        has_more=data.get("has_more", False),
                        next_cursor=data.get("next_cursor"),
                    ),
                )
            return _upstream_err(SearchNotionResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(SearchNotionResult, tlog, exc)

    @mcp.tool(
        name="get_page",
        description="Retrieve a Notion page by ID with properties and metadata",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_page(
        page_id: str = Field(description="Notion page ID (UUID) to retrieve."),
    ) -> GetPageResult:
        tlog = ToolLogger(logger, "get_page")
        try:
            data, status, retry_after = service.notion_request(
                "GET",
                f"/v1/pages/{page_id}",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if 200 <= status < 300:
                tlog.success()
                return GetPageResult(
                    success=True, statusCode=status, data=PageData(**data)
                )
            return _upstream_err(GetPageResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(GetPageResult, tlog, exc)

    @mcp.tool(
        name="fetch_page_content",
        description="Retrieve a Notion page with its full content including all child blocks and properties",
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def fetch_page_content(
        page_id: str = Field(description="Notion page ID (UUID) to fetch content for."),
        include_children: bool = Field(
            default=True,
            description="Whether to fetch and include the page's child blocks.",
        ),
        recursive: bool = Field(
            default=False,
            description="Recursively fetch nested children of child blocks, up to max_depth.",
        ),
        max_depth: int = Field(
            default=3, description="Maximum recursion depth when recursive=True."
        ),
        page_size: int = Field(
            default=100,
            description="Number of child blocks to fetch per page when recursive=False (max 100).",
        ),
        start_cursor: str | None = Field(
            default=None,
            description="Cursor from a previous response to page through child blocks (non-recursive only).",
        ),
    ) -> FetchPageContentResult:
        tlog = ToolLogger(logger, "fetch_page_content")
        try:
            page_data, status, retry_after = service.notion_request(
                "GET",
                f"/v1/pages/{page_id}",
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if not (200 <= status < 300):
                return _upstream_err(
                    FetchPageContentResult, tlog, status, page_data, retry_after
                )

            has_more_children: bool | None = None
            next_cursor: str | None = None
            children_count: int | None = None

            if include_children:
                if recursive:
                    logger.info(
                        "Fetching children recursively (max_depth=%d)", max_depth
                    )
                    all_children = _fetch_block_children_recursive(
                        page_id, max_depth=max_depth
                    )
                    page_data["children"] = all_children
                    has_more_children = False
                    next_cursor = None
                    children_count = len(all_children)
                else:
                    params = {"page_size": min(page_size, 100)}
                    if start_cursor:
                        params["start_cursor"] = start_cursor

                    children_data, children_status, _ = service.notion_request(
                        "GET",
                        f"/v1/blocks/{page_id}/children",
                        params=params,
                        timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                    )

                    if 200 <= children_status < 300:
                        page_data["children"] = children_data.get("results", [])
                        has_more_children = children_data.get("has_more", False)
                        next_cursor = children_data.get("next_cursor")
                        children_count = len(page_data["children"])
                        logger.info("Retrieved %d child blocks", children_count)
                    else:
                        logger.error(
                            "Failed to fetch children: HTTP %s", children_status
                        )

            tlog.success()
            return FetchPageContentResult(
                success=True,
                statusCode=status,
                data=FetchPageContentData(
                    page_id=page_data.get("id"),
                    title=_extract_title(page_data),
                    content=_extract_plain_text(page_data.get("children", [])),
                    url=page_data.get("url"),
                    has_more_children=has_more_children,
                    next_cursor=next_cursor,
                    children_count=children_count,
                ),
            )
        except Exception as exc:
            return _handle_request_exc(FetchPageContentResult, tlog, exc)

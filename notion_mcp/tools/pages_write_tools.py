"""Pages write group: create_page_under_page, create_workspace_page, update_page, append_text_block."""

import logging
from typing import Literal

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas import (
    AppendTextBlockData,
    AppendTextBlockResult,
    BlockData,
    CreatePageUnderPageData,
    CreatePageUnderPageResult,
    CreateWorkspacePageData,
    CreateWorkspacePageResult,
    PageData,
    UpdatePageData,
    UpdatePageResult,
)
from ._helpers import _err, _handle_request_exc, _upstream_err

logger = logging.getLogger("notion-mcp.tools.pages_write")


def _build_create_page_body(
    *,
    parent: dict,
    title: str | None = None,
    properties: dict | None = None,
    position: dict | None = None,
) -> dict:
    """Build a Notion /v1/pages create-page request body.

    Ported verbatim from the legacy tools/write_operations.py
    ._build_create_page_body — note `properties` is accepted but not
    folded into the body, matching the legacy behavior exactly.
    """

    body: dict = {"parent": parent}

    if title is not None:
        body["properties"] = {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        }

    if position:
        body["position"] = position

    return body


def register_pages_write_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="create_page_under_page",
        description="Create a new page under a parent page",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_page_under_page(
        parent_page_id: str = Field(
            description="The ID of the parent page this new page will be created under."
        ),
        title: str | None = Field(
            default="Untitled New page Created",
            description="The title for the new page. Defaults to 'Untitled New page Created' if omitted.",
        ),
        position: dict | None = Field(
            default=None,
            description='Insert postion. strict Format:{"type": "page_end"} or {"type": "page_start"} ',
        ),
    ) -> CreatePageUnderPageResult:
        tlog = ToolLogger(logger, "create_page_under_page")
        try:
            parent = {"page_id": parent_page_id, "type": "page_id"}
            body = _build_create_page_body(parent=parent, title=title, position=position)

            data, status, retry_after = service.notion_request("POST", "/v1/pages", body=body)
            if 200 <= status < 300:
                tlog.success()
                return CreatePageUnderPageResult(
                    success=True, statusCode=status, data=CreatePageUnderPageData(**data)
                )
            return _upstream_err(CreatePageUnderPageResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CreatePageUnderPageResult, tlog, exc)

    @mcp.tool(
        name="create_workspace_page",
        description="Create a new page at a workspace level (without parent page)",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_workspace_page(
        title: str | None = Field(
            default="Untitled New page Created",
            description="The title for the new page. Defaults to 'Untitled New page Created' if omitted.",
        ),
    ) -> CreateWorkspacePageResult:
        tlog = ToolLogger(logger, "create_workspace_page")
        try:
            parent = {"type": "workspace", "workspace": True}
            body = _build_create_page_body(parent=parent, title=title)

            data, status, retry_after = service.notion_request("POST", "/v1/pages", body=body)
            if 200 <= status < 300:
                tlog.success()
                return CreateWorkspacePageResult(
                    success=True, statusCode=status, data=CreateWorkspacePageData(**data)
                )
            return _upstream_err(CreateWorkspacePageResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(CreateWorkspacePageResult, tlog, exc)

    @mcp.tool(
        name="update_page",
        description=(
            "Update an existing Notion page's properties and metadata. "
            "Providing `properties`, `icon`, `cover`, or other fields replaces the corresponding "
            "current values rather than merging with them — the original state is not stored by "
            "the API after the call. Call get_page first to see current property values before "
            "updating. The response includes both the before and after state so you have a full "
            "record of what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_page(
        page_id: str = Field(description="The ID of the Notion page to update."),
        properties: dict | None = Field(
            default=None,
            description="A dict of Notion page property updates keyed by property name; replaces the corresponding existing property values rather than merging with them. Omit to leave properties unchanged.",
        ),
        icon: dict | None = Field(
            default=None,
            description="A Notion file, emoji, or external object to set as the page icon. Omit to leave the icon unchanged.",
        ),
        cover: dict | None = Field(
            default=None,
            description="A Notion file or external object to set as the page cover image. Omit to leave the cover unchanged.",
        ),
        archived: bool | None = Field(
            default=None,
            description="Whether to archive (true) or restore (false) the page. Omit to leave archival state unchanged.",
        ),
        in_trash: bool | None = Field(
            default=None,
            description="Whether to move the page to (true) or restore it from (false) the trash. Omit to leave trash state unchanged.",
        ),
        is_locked: bool | None = Field(
            default=None,
            description="Whether to lock (true) or unlock (false) the page to prevent further edits. Omit to leave the lock state unchanged.",
        ),
        template: dict | None = Field(
            default=None,
            description="A Notion page template object to reapply to the page. Omit to leave the current template unchanged.",
        ),
        erase_content: bool | None = Field(
            default=None,
            description="Whether to clear the page's existing block content before applying the update. Omit to leave existing content in place.",
        ),
    ) -> UpdatePageResult:
        tlog = ToolLogger(logger, "update_page")
        try:
            before_data, before_status, _ = service.notion_request("GET", f"/v1/pages/{page_id}")
            if not (200 <= before_status < 300):
                return _upstream_err(UpdatePageResult, tlog, before_status, before_data)

            body: dict = {}
            if properties is not None:
                body["properties"] = properties
            if icon is not None:
                body["icon"] = icon
            if cover is not None:
                body["cover"] = cover
            if is_locked is not None:
                body["is_locked"] = is_locked
            if template is not None:
                body["template"] = template
            if erase_content is not None:
                body["erase_content"] = erase_content
            if archived is not None:
                body["archived"] = archived
            if in_trash is not None:
                body["in_trash"] = in_trash

            if not body:
                return _err(
                    UpdatePageResult, tlog, "VALIDATION_ERROR",
                    "At least one update parameter must be provided", 400,
                )

            after_data, after_status, retry_after = service.notion_request(
                "PATCH", f"/v1/pages/{page_id}", body=body
            )
            if not (200 <= after_status < 300):
                return _upstream_err(UpdatePageResult, tlog, after_status, after_data, retry_after)

            tlog.success()
            return UpdatePageResult(
                success=True,
                statusCode=after_status,
                data=UpdatePageData(before=PageData(**before_data), after=PageData(**after_data)),
            )
        except Exception as exc:
            return _handle_request_exc(UpdatePageResult, tlog, exc)

    @mcp.tool(
        name="append_text_block",
        description="Append a text block to a page ",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def append_text_block(
        block_id: str = Field(description="The ID could be page ID or parent block ID"),
        type: Literal[
            "paragraph",
            "heading_1",
            "heading_2",
            "heading_3",
            "bulleted_list_item",
            "numbered_list_item",
            "to_do",
            "toggle",
            "quote",
            "callout",
        ] = Field(description="The type of text block to create"),
        content: str = Field(description="The text content for the block"),
        checked: bool | None = Field(
            default=None, description="For to_do blocks only - whether the item is checked"
        ),
        color: str | None = Field(
            default=None,
            description="text color or background color. available colors : [ 'default', 'gray', 'brown', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'red'] background color format : eg. red_background or blue_background ",
        ),
        position: Literal["end", "start"] | None = Field(
            default=None, description="Position to insert the new block; "
        ),
    ) -> AppendTextBlockResult:
        tlog = ToolLogger(logger, "append_text_block")
        try:
            block: dict = {
                "object": "block",
                "type": type,
                type: {
                    "rich_text": [
                        {"type": "text", "text": {"content": content}},
                    ]
                },
            }

            if type == "to_do" and checked is not None:
                block[type]["checked"] = checked

            if color:
                block[type]["color"] = color

            body: dict = {"children": [block]}

            if position:
                body["position"] = {"type": position}

            data, status, retry_after = service.notion_request(
                "PATCH", f"/v1/blocks/{block_id}/children", body=body
            )
            if 200 <= status < 300:
                tlog.success()
                return AppendTextBlockResult(
                    success=True,
                    statusCode=status,
                    data=AppendTextBlockData(blocks=[BlockData(**b) for b in data.get("results", [])]),
                )
            return _upstream_err(AppendTextBlockResult, tlog, status, data, retry_after)
        except Exception as exc:
            return _handle_request_exc(AppendTextBlockResult, tlog, exc)

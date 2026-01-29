"""
Stateless MCP Server for Notion API
"""

import logging
import argparse
from typing import Dict, Optional, Literal
from fastmcp import FastMCP
from pydantic import Field

from tools import (
    search_notion_service,
    get_page_service,
    fetch_page_content_service,
    create_page_under_page_service,
    update_page_service,
    get_database_service,
    query_data_source_service,
    get_data_source_service,
    create_database_service,
    list_users_service,
    get_user_service,
    get_self_service,
    create_workspace_page_service,
    append_text_block_service,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("notion-mcp-server")

#  FastMCP instance
mcp = FastMCP("Notion MCP Server")


# ============== Read Operations ==============


@mcp.tool(
    name="search_notion",
    description="Search all pages and databases by title or list all pages  ",
)
def search_notion(
    oauth_token: str,
    query: str = Field(
        default="", description="Search query string, keep it empty to list all pages"
    ),
    filter_type: str | None = Field(
        default=None, description="Filter by 'page' or 'data_source'. "
    ),
    page_size: int = Field(
        default=20, description="Number of pages to return (max 100)"
    ),
    start_cursor: str | None = None,
):
    return search_notion_service(
        oauth_token, query, filter_type, page_size, start_cursor
    )


@mcp.tool(
    name="get_page",
    description="Retrieve a Notion page by ID with properties and metadata",
)
def get_page(oauth_token: str, page_id: str):
    return get_page_service(oauth_token, page_id)


@mcp.tool(
    name="fetch_page_content",
    description="Retrieve a Notion page with its full content including all child blocks and properties",
)
def fetch_page_content(
    oauth_token: str,
    page_id: str,
    include_children: bool = True,
    recursive: bool = False,
    max_depth: int = 3,
    page_size: int = 100,
    start_cursor: str | None = None,
):
    return fetch_page_content_service(
        oauth_token,
        page_id,
        include_children,
        recursive,
        max_depth,
        page_size,
        start_cursor,
    )


# ============== Write Operations ==============


@mcp.tool(
    name="create_page_under_page",
    description="Create a new page under a parent page",
)
def create_page_under_page(
    oauth_token: str,
    parent_page_id: str,
    title: str | None = "Untitled New page Created",
    position: Optional[Dict] | None = Field(
        default=None,
        description='Insert postion. strict Format:{"type": "page_end"} or {"type": "page_start"} ',
    ),
):
    return create_page_under_page_service(
        oauth_token,
        parent_page_id,
        title,
        position,
    )


@mcp.tool(
    name="create_workspace_page",
    description="Create a new page at a workspace level (without parent page)",
)
def create_workspace_page(
    oauth_token: str,
    title: str | None = "Untitled New page Created",
):
    return create_workspace_page_service(
        oauth_token,
        title,
    )


@mcp.tool(
    name="update_page",
    description="Update an existing Notion page's properties and metadata.",
)
def update_page(
    oauth_token: str,
    page_id: str,
    properties: dict | None = None,
    icon: dict | None = None,
    cover: dict | None = None,
    archived: bool | None = None,
    in_trash: bool | None = None,
    is_locked: bool | None = None,
    template: dict | None = None,
    erase_content: bool | None = None,
):
    return update_page_service(
        oauth_token,
        page_id,
        properties,
        icon,
        cover,
        archived,
        in_trash,
        is_locked,
        template,
        erase_content,
    )


@mcp.tool(
    name="append_text_block",
    description="Append a text block to a page ",
)
def append_text_block(
    oauth_token: str,
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
    checked: Optional[bool] = Field(
        default=None, description="For to_do blocks only - whether the item is checked"
    ),
    color: Optional[str] = Field(
        default=None,
        description="text color or background color. available colors : [ 'default', 'gray', 'brown', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'red'] background color format : eg. red_background or blue_background ",
    ),
    position: Literal["end", "start"] | None = Field(
        default=None, description="Position to insert the new block; "
    ),
):
    return append_text_block_service(
        oauth_token, block_id, type, content, checked, color, position
    )


########## Databse Tools ##########


@mcp.tool(
    name="get_database",
    description="Retrieve a database object by ID with title, parent, and data sources",
)
def get_database(oauth_token: str, database_id: str):
    return get_database_service(oauth_token, database_id)


@mcp.tool(
    name="get_data_source",
    description="Retrieve a data source (database schema/properties) by ID",
)
def get_data_source(oauth_token: str, data_source_id: str):
    return get_data_source_service(oauth_token, data_source_id)


@mcp.tool(
    name="query_data_source",
    description="Query a data source to get pages with optional filtering and sorting",
)
def query_data_source(
    oauth_token: str,
    data_source_id: str,
    filter: dict | None = None,
    sorts: list | None = None,
    page_size: int = 100,
    start_cursor: str | None = None,
):
    return query_data_source_service(
        oauth_token, data_source_id, filter, sorts, page_size, start_cursor
    )


@mcp.tool(
    name="create_database",
    description="Create a new database as a child of an existing page",
)
def create_database(
    oauth_token: str,
    parent_id: str,
    title: str = "Untitled Database",
    description: str | None = None,
    properties: dict | None = None,
    is_inline: bool = False,
    icon: dict | None = None,
    cover: dict | None = None,
):
    return create_database_service(
        oauth_token, parent_id, title, description, properties, is_inline, icon, cover
    )


########## User Tools ##########


@mcp.tool(
    name="list_users",
    description="List all users in the workspace (guests not included)",
)
def list_users(
    oauth_token: str,
    page_size: int = 100,
    start_cursor: str | None = None,
):
    return list_users_service(oauth_token, page_size, start_cursor)


@mcp.tool(
    name="get_user",
    description="Retrieve a specific user by their ID",
)
def get_user(oauth_token: str, user_id: str):
    return get_user_service(oauth_token, user_id)


@mcp.tool(
    name="get_self",
    description="Retrieve the bot user associated with your API token, including owner and workspace info",
)
def get_self(oauth_token: str):
    return get_self_service(oauth_token)


########## parsing Argus ##########


def parse_args():
    parser = argparse.ArgumentParser(description="Notion MCP Server")
    parser.add_argument(
        "-t",
        "--transport",
        help="Transport method: 'stdio', 'sse', or 'streamable-http'",
        default="streamable-http",
    )
    parser.add_argument("--host", help="Host to bind to", default="0.0.0.0")
    parser.add_argument("--port", type=int, help="Port to bind to", default=8000)
    return parser.parse_args()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Notion MCP Server Starting (Stateless Multi-User)")
    logger.info("=" * 60)

    args = parse_args()

    run_kwargs = {}
    if args.transport:
        run_kwargs["transport"] = args.transport
    if args.host:
        run_kwargs["host"] = args.host
    if args.port:
        run_kwargs["port"] = args.port

    try:
        mcp.run(**run_kwargs)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        raise

"""
Stateless MCP Server for Notion API
"""

import logging
import argparse
from typing import Literal
from fastmcp import FastMCP

from tools import (
    search_notion_service,
    get_page_service,
    notion_fetch_service,
    create_page_service,
    update_page_service,
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
    description="Search all pages and databases shared with the integration by title",
)
def search_notion(
    oauth_token: str,
    query: str = "",
    filter_type: str | None = None,
    page_size: int = 10,
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
    name="notion_fetch",
    description="Retrieve a Notion page with its full content including all child blocks and properties",
)
def notion_fetch(
    oauth_token: str,
    page_id: str,
    include_children: bool = True,
    recursive: bool = False,
    max_depth: int = 3,
    page_size: int = 100,
    start_cursor: str | None = None,
):
    return notion_fetch_service(
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
    name="create_page",
    description="Create a new page in a database or under a parent page",
)
def create_page(
    oauth_token: str,
    parent_id: str,
    parent_type: Literal["data_source_id", "page_id"] = "page_id",
    title: str = "Untitled",
    properties: dict | None = None,  # required for data source
    children: list | None = None,
    icon: dict | None = None,
    cover: dict | None = None,
    template: dict | None = None,
    position: dict | None = None,
):
    return create_page_service(
        oauth_token,
        parent_id,
        parent_type,
        title,
        properties,
        children,
        icon,
        cover,
        template,
        position,
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


########## parsing Argus ##########


def parse_args():
    parser = argparse.ArgumentParser(description="Notion MCP Server")
    parser.add_argument(
        "-t",
        "--transport",
        help="Transport method: 'stdio', 'sse', or 'streamable-http'",
        default="streamable-http",
    )
    parser.add_argument("--host", help="Host to bind to", default="localhost")
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

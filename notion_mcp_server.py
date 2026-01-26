"""
Stateless MCP Server for Notion API
"""

import logging
import argparse

from fastmcp import FastMCP

from tools import (
    search_notion_service,
    get_page_service,
    notion_fetch_service,
    create_page_service,
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
    """
    Search Notion pages and databases.

    Args:
        oauth_token: User's Notion OAuth access token
        query: Search query string
        filter_type: "page" or "database" (optional)
        page_size: Results per page (max 100)
        start_cursor: Pagination cursor

    Returns:
        Dictionary with search results including pages/databases that match the query
    """
    return search_notion_service(
        oauth_token, query, filter_type, page_size, start_cursor
    )


@mcp.tool(
    name="get_page",
    description="Retrieve a Notion page by ID with properties and metadata",
)
def get_page(oauth_token: str, page_id: str):
    """
    Get the page details by notion page ID with properties and metadata.

    Args:
        oauth_token: User's Notion OAuth access token
        page_id: The ID of the page to retrieve

    Returns:
        A dictionary containing the page details or an error message if page not found.
    """
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
    """
    Fetch complete page data including properties and content blocks.

    This tool retrieves both the page metadata/properties and its child blocks (content).
    Use this when you need to read the actual content of a page, not just its properties.

    Args:
        oauth_token: User's Notion OAuth access token
        page_id: The ID of the page to fetch
        include_children: Whether to include child blocks (page content), defaults to True
        recursive: Whether to recursively fetch nested children blocks (e.g., toggle lists, columns), defaults to False
        max_depth: Maximum recursion depth when recursive=True (prevents infinite loops), defaults to 3
        page_size: Number of child blocks to retrieve per request (max 100), defaults to 100
        start_cursor: Pagination cursor for retrieving more child blocks (only used when recursive=False)

    Returns:
        Dictionary containing page properties, child blocks, and pagination info.
        When recursive=True, all nested children are included in a 'children' array within each block.
        When recursive=False, includes 'has_more_children' and 'next_cursor' for pagination.
    """
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
    parent_type: str = "page_id",
    title: str = "Untitled",
    properties: dict | None = None,
    children: list | None = None,
    icon: dict | None = None,
    cover: dict | None = None,
):
    """
    Create a new page in a database or under a parent page.

    Args:
        oauth_token: User's Notion OAuth access token
        parent_id: The ID of the parent database or page
        parent_type: The type of the parent ("database_id" or "page_id"), defaults to "page_id"
        title: The title of the new page (used when parent is a page)
        properties: A dictionary of properties for the new page (required for database pages)
        children: Optional list of child blocks to include in the new page
        icon: Optional icon for the page (emoji or external URL)
        cover: Optional cover image for the page (external URL or uploaded file)

    Returns:
        A dictionary containing the newly created page details or an error message.
    """
    return create_page_service(
        oauth_token, parent_id, parent_type, title, properties, children, icon, cover
    )


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

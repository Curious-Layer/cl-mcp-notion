"""
Stateless MCP Server for Notion API

"""

import logging
import argparse
from typing import Dict, List
from typing import Optional

import requests
from fastmcp import FastMCP

# Notion API configuration
NOTION_API_BASE = "https://api.notion.com"
NOTION_VERSION = "2025-09-03"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("notion-mcp-server")

# Create FastMCP instance
mcp = FastMCP("Notion MCP Server")


def _get_headers(oauth_token: str) -> Dict[str, str]:
    """Create headers for Notion API requests - stateless per request"""
    return {
        "Authorization": f"Bearer {oauth_token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _make_request(
    method: str,
    endpoint: str,
    oauth_token: str,
    body: Dict | None = None,
    params: Dict | None = None,
) -> Dict:
    """Generic request handler for Notion API"""
    headers = _get_headers(oauth_token)
    url = f"{NOTION_API_BASE}{endpoint}"

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=body,
            params=params,
        )
        result = response.json()

        if not (200 <= response.status_code < 300):
            logger.error(f"Notion API error: {result}")
            return {
                "error": result.get("message", "Unknown error"),
                "code": result.get("code"),
                "status": response.status_code,
            }
        return result

    except Exception as e:
        logger.error(f"Request error: {e}")
        return {"error": str(e)}


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
) -> Dict:
    """
    Search Notion pages and databases.

    Args:
        oauth_token: User's Notion OAuth access token
        query: Search query string
        filter_type: "page" or "database" (optional)
        page_size: Results per page (max 100)
        start_cursor: Pagination cursor
    """
    logger.info(f"[search_notion] query='{query}'")

    body = {"query": query, "page_size": min(page_size, 100)}

    if filter_type in ["page", "data_source"]:
        body["filter"] = {"property": "object", "value": filter_type}

    if start_cursor:
        body["start_cursor"] = start_cursor

    return _make_request("POST", "/v1/search", oauth_token, body=body)


@mcp.tool(
    name="get_page",
    description="Retrieve a Notion page by ID with properties adn metadata",
)
def get_page(oauth_token: str, page_id: str) -> Dict:
    """
    Get the page details by notion page ID with properties and metadata.
    Args:
        oauth_token: User's Notion OAuth access token
        page_id: The ID of the page to retrieve
    Returns:
        A dictionary containing the page details or an error message if not page not found.
    """

    logger.info(f"[get_page] page_id='{page_id}'")

    result = _make_request("GET", f"/v1/pages/{page_id}", oauth_token)

    if "error" in result:
        logger.error(f"Failed to retrieve page: {page_id}: {result.get('error')}")
    else:
        logger.info(f"Successfully retrieved page: {page_id}")

    return result


############################# Write Operations ################################
@mcp.tool(
    name="create_page",
    description="Create a new page in a database or under a parent page",
)
def create_page(
    oauth_token: str,
    parent_id: str,
    parent_type: str = "page_id",
    title: str = "Untitled",
    properties: Optional[Dict] = None,
    children: Optional[List] = None,
    icon: Optional[Dict] = None,
    cover: Optional[Dict] = None,
) -> Dict:
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
    logger.info(
        f"[create_page] parent_id={parent_id}, parent_type={parent_type}, title={title}"
    )

    if parent_type not in ["page_id", "database_id"]:
        logger.error(f"Invalid parent_type: {parent_type}")
        return {"error": "parent_type must be either 'page_id' or 'database_id'"}

    body = {"parent": {parent_type: parent_id, "type": parent_type}}

    if parent_type == "page_id":
        # When creating under a page, use title property
        if not properties:
            properties = {
                "title": {"title": [{"type": "text", "text": {"content": title}}]}
            }
        body["properties"] = properties
    elif parent_type == "database_id":
        # When creating in a database, properties are required
        if not properties:
            logger.error("properties are required when creating a page in a database")
            return {
                "error": "properties are required when parent_type is 'database_id'"
            }
        body["properties"] = properties

    if children:
        body["children"] = children

    if icon:
        body["icon"] = icon

    if cover:
        body["cover"] = cover

    result = _make_request("POST", "/v1/pages", oauth_token, body=body)

    if "error" in result:
        logger.error(f"Failed to create page: {result.get('error')}")
    else:
        logger.info(f"Successfully created page: {result.get('id')}")

    return result


# Function for parsing cmd-line arguments
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

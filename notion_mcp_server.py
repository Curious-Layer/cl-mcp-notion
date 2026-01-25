"""
Stateless MCP Server for Notion API

"""

import logging
import argparse
from typing import Dict

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

        if response.status_code != 200:
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


# ============== MCP TOOLS ==============


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

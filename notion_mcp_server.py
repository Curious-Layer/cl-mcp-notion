"""
MCP Server for Notion API
Provides access to Notion operations through Model Context Protocol
"""

import logging
import argparse
from typing import Dict

import requests
from fastmcp import FastMCP

# Notion API configuration
NOTION_API_BASE = "https://api.notion.com"
NOTION_VERSION = "2025-09-03"

#  logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("notion-mcp-server")

# Create FastMCP instance
mcp = FastMCP("Notion MCP Server")


def _get_headers(oauth_token: str) -> Dict[str, str]:
    """Create headers for Notion API requests"""
    return {
        "Authorization": f"Bearer {oauth_token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


# Define MCP Tools


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
    Search Notion pages and databases by title.

    Args:
        oauth_token: The user's Notion OAuth access token
        query: Search query string (searches titles)
        filter_type: Filter by object type - "page" or "database" (optional)
        page_size: Number of results to return (max 100)
        start_cursor: Pagination cursor for next page of results
    """
    logger.info(f"Executing search_notion with query: {query}")
    try:
        headers = _get_headers(oauth_token)

        body = {
            "query": query,
            "page_size": min(page_size, 100),
        }

        if filter_type and filter_type in ["page", "database"]:
            body["filter"] = {"property": "object", "value": filter_type}

        if start_cursor:
            body["start_cursor"] = start_cursor

        response = requests.post(
            f"{NOTION_API_BASE}/v1/search",
            headers=headers,
            json=body,
        )

        result = response.json()

        if response.status_code != 200:
            logger.error(f"Notion API error: {result}")
            return {
                "error": result.get("message", "Unknown error"),
                "code": result.get("code"),
            }

        logger.info(f"Found {len(result.get('results', []))} results")
        return result

    except Exception as e:
        logger.error(f"Error in search_notion: {e}")
        return {"error": str(e)}


# Function for parsing the cmd-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Notion MCP Server")
    parser.add_argument(
        "-t",
        "--transport",
        help="Transport method for MCP (Allowed Values: 'stdio', 'sse', or 'streamable-http')",
        default=None,
    )
    parser.add_argument("--host", help="Host to bind the server to", default=None)
    parser.add_argument(
        "--port", type=int, help="Port to bind the server to", default=None
    )
    return parser.parse_args()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Notion MCP Server Starting")
    logger.info("=" * 60)

    args = parse_args()

    run_kwargs = {}
    if args.transport:
        run_kwargs["transport"] = args.transport
        logger.info(f"Transport: {args.transport}")
    if args.host:
        run_kwargs["host"] = args.host
        logger.info(f"Host: {args.host}")
    if args.port:
        run_kwargs["port"] = args.port
        logger.info(f"Port: {args.port}")

    try:
        mcp.run(**run_kwargs)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        raise

"""User operation tools for Notion API"""

import logging
from typing import Dict, Optional

from utils import make_notion_request

logger = logging.getLogger("notion-mcp-server")


def get_users_service(
    oauth_token: str,
    page_size: int = 100,
    start_cursor: Optional[str] = None,
) -> Dict:
    """
    List all users in the workspace. Guests are not included in the response.
    Returns:
        A paginated list of user objects.
    """
    logger.info("[list_users_service] Fetching users")

    params = {"page_size": min(page_size, 100)}

    if start_cursor:
        params["start_cursor"] = start_cursor
        logger.info(f"Using cursor: {start_cursor[:20]}...")

    result = make_notion_request("GET", "/v1/users", oauth_token, params=params)

    if "error" in result:
        logger.error(f"Failed to list users: {result.get('error')}")
    else:
        results_count = len(result.get("results", []))
        has_more = result.get("has_more", False)
        logger.info(f"Retrieved {results_count} user(s), has_more={has_more}")

    return result

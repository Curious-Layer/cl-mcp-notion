"""User operation tools for Notion API"""

import logging
from typing import Dict, Optional

from utils import make_notion_request

logger = logging.getLogger("notion-mcp-server")


def list_users_service(
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


def get_user_service(oauth_token: str, user_id: str) -> Dict:
    """
    Returns:
        A user object containing id, name, avatar_url, and type (person or bot).
    """
    logger.info(f"[get_user_service] user_id='{user_id}'")

    result = make_notion_request("GET", f"/v1/users/{user_id}", oauth_token)

    if "error" in result:
        logger.error(f"Failed to retrieve user: {user_id}: {result.get('error')}")
    else:
        user_type = result.get("type", "unknown")
        user_name = result.get("name", "Unknown")
        logger.info(f"Successfully retrieved user: {user_name} (type={user_type})")

    return result


def get_self_service(oauth_token: str) -> Dict:
    """
    Returns:
        A bot user object with owner, workspace_id, workspace_limits, and workspace_name.
    """
    logger.info("[get_self_service] Fetching bot user info")

    result = make_notion_request("GET", "/v1/users/me", oauth_token)

    if "error" in result:
        logger.error(f"Failed to retrieve bot user: {result.get('error')}")
    else:
        bot_name = result.get("name", "Unknown Bot")
        workspace_name = result.get("bot", {}).get(
            "workspace_name", "Unknown Workspace"
        )
        logger.info(
            f"Successfully retrieved bot: {bot_name} (workspace={workspace_name})"
        )

    return result

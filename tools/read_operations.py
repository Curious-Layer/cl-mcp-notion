"""Read operation implementations for Notion API"""

import logging
from typing import Dict, Optional

from utils import make_notion_request

logger = logging.getLogger("notion-mcp-server")


def search_notion_service(
    oauth_token: str,
    query: str = "",
    filter_type: Optional[str] = None,
    page_size: int = 10,
    start_cursor: Optional[str] = None,
) -> Dict:
    """Implementation of search_notion tool"""
    logger.info(f"[search_notion] query='{query}'")

    body = {"query": query, "page_size": min(page_size, 100)}

    if filter_type in ["page", "data_source"]:
        body["filter"] = {"property": "object", "value": filter_type}

    if start_cursor:
        body["start_cursor"] = start_cursor

    return make_notion_request("POST", "/v1/search", oauth_token, body=body)


def get_page_service(oauth_token: str, page_id: str) -> Dict:
    """Implementation of get_page tool"""
    logger.info(f"[get_page] page_id='{page_id}'")

    result = make_notion_request("GET", f"/v1/pages/{page_id}", oauth_token)

    if "error" in result:
        logger.error(f"Failed to retrieve page: {page_id}: {result.get('error')}")
    else:
        logger.info(f"Successfully retrieved page: {page_id}")

    return result

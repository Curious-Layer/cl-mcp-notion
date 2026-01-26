"""Write operation tools for Notion API"""

import logging
from typing import Dict, List, Optional

from utils import make_notion_request

logger = logging.getLogger("notion-mcp-server")


def create_page_service(
    oauth_token: str,
    parent_id: str,
    parent_type: str = "page_id",
    title: str = "Untitled",
    properties: Optional[Dict] = None,
    children: Optional[List] = None,
    icon: Optional[Dict] = None,
    cover: Optional[Dict] = None,
) -> Dict:
    logger.info(
        f"[create_page_service] parent_id={parent_id}, parent_type={parent_type}, title={title}"
    )

    if parent_type not in ["page_id", "database_id"]:
        logger.error(f"Invalid parent_type: {parent_type}")
        return {"error": "parent_type must be either 'page_id' or 'database_id'"}

    body = {"parent": {parent_type: parent_id, "type": parent_type}}

    if parent_type == "page_id":
        if not properties:
            properties = {
                "title": {"title": [{"type": "text", "text": {"content": title}}]}
            }
        body["properties"] = properties
    elif parent_type == "database_id":
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

    result = make_notion_request("POST", "/v1/pages", oauth_token, body=body)

    if "error" in result:
        logger.error(f"Failed to create page: {result.get('error')}")
    else:
        logger.info(f"Successfully created page: {result.get('id')}")

    return result

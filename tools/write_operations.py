"""Write operation tools for Notion API"""

import logging
from typing import Dict, List, Optional

from utils import make_notion_request

logger = logging.getLogger("notion-mcp-server")


def create_page_service(
    oauth_token: str,
    parent_id: str,
    parent_type: str = "page_id",  # "page_id" or "data_source_id"
    title: str = "Untitled",
    properties: Optional[Dict] = None,  # required when creating a page in a data source
    children: Optional[List] = None,  # list of child blocks to include in the new page
    icon: Optional[Dict] = None,
    cover: Optional[Dict] = None,
) -> Dict:
    logger.info(
        f"[create_page_service] parent_id={parent_id}, parent_type={parent_type}, title={title}"
    )

    if parent_type not in ["page_id", "data_source_id"]:
        logger.error(f"Invalid parent_type: {parent_type}")
        return {"error": "parent_type must be either 'page_id' or 'data_source_id'"}

    body = {"parent": {parent_type: parent_id, "type": parent_type}}

    if parent_type == "page_id":
        if not properties:
            properties = {
                "title": {"title": [{"type": "text", "text": {"content": title}}]}
            }
        body["properties"] = properties
    elif parent_type == "data_source_id":
        if not properties:
            logger.error("properties are required when creating a page in a database")
            return {
                "error": "properties are required when parent_type is 'data_source_id'"
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


def update_page_service(
    oauth_token: str,
    page_id: str,
    properties: Optional[Dict] = None,
    icon: Optional[Dict] = None,
    cover: Optional[Dict] = None,
    archived: Optional[bool] = None,
    in_trash: Optional[bool] = None,
    is_locked: Optional[bool] = None,
    template: Optional[Dict] = None,
    erase_content: Optional[bool] = None,
) -> Dict:
    logger.info(f"[update_page_service] page_id='{page_id}'")

    body = {}

    if properties is not None:
        body["properties"] = properties
        logger.info(f"Updating {len(properties)} properties")

    if icon is not None:
        body["icon"] = icon
        logger.info(f"Setting icon: type={icon.get('type')}")

    if cover is not None:
        body["cover"] = cover
        logger.info(f"Setting cover: type={cover.get('type')}")

    if is_locked is not None:
        body["is_locked"] = is_locked
        logger.info(f"Setting is_locked={is_locked}")

    if template is not None:
        body["template"] = template
        logger.info(f"Setting template: {template.get('type')}")

    if erase_content is not None:
        body["erase_content"] = erase_content
        logger.info(f"Setting erase_content={erase_content}")

    if archived is not None:
        body["archived"] = archived
        logger.info(f"Setting archived={archived}")

    if in_trash is not None:
        body["in_trash"] = in_trash
        logger.info(f"Setting in_trash={in_trash}")

    if not body:
        logger.warning("No updates provided for page")
        return {"error": "At least one update parameter must be provided"}

    result = make_notion_request(
        "PATCH", f"/v1/pages/{page_id}", oauth_token, body=body
    )

    if "error" in result:
        logger.error(f"Failed to update page: {result.get('error')}")
    else:
        logger.info(f"Successfully updated page: {page_id}")

    return result

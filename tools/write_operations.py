"""Write operation tools for Notion API"""

import logging
from typing import Dict, Optional

from utils import make_notion_request

logger = logging.getLogger("notion-mcp-server")


def _build_create_page_body(
    *,
    parent: Dict,
    title: Optional[str] = None,
    properties: Optional[Dict] = None,
    position: Optional[Dict] = None,
) -> Dict:
    """
    validates the notion create page payload.

    """

    # if template and (children or content):
    #     raise ToolError("children/content cannot be provided when using a template")

    body: Dict = {"parent": parent}

    if title is not None:
        body["properties"] = {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        }

    if position:
        body["position"] = position

    return body


def create_page_under_page_service(
    oauth_token: str,
    parent_page_id: str,
    title: str = "Untitled",
    position: Optional[Dict] = None,
) -> Dict:
    parent = {"page_id": parent_page_id, "type": "page_id"}

    body = _build_create_page_body(
        parent=parent,
        title=title,
        position=position,
    )

    result = make_notion_request("POST", "/v1/pages", oauth_token, body=body)

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

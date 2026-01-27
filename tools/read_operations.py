"""Read operation implementations for Notion API"""

import logging
from typing import Dict, Optional

from utils import make_notion_request

logger = logging.getLogger("notion-mcp-server")


########### Search Notion Service #############
def search_notion_service(
    oauth_token: str,
    query: str = "",
    filter_type: Optional[str] = None,
    page_size: int = 10,
    start_cursor: Optional[str] = None,
) -> Dict:
    logger.info(f"[search_notion] query='{query}'")

    body = {"query": query, "page_size": min(page_size, 100)}

    if filter_type in ["page", "data_source"]:
        body["filter"] = {"property": "object", "value": filter_type}

    if start_cursor:
        body["start_cursor"] = start_cursor

    return make_notion_request("POST", "/v1/search", oauth_token, body=body)


############## Get Page Service #############
def get_page_service(oauth_token: str, page_id: str) -> Dict:
    logger.info(f"[get_page] page_id='{page_id}'")

    result = make_notion_request("GET", f"/v1/pages/{page_id}", oauth_token)

    if "error" in result:
        logger.error(f"Failed to retrieve page: {page_id}: {result.get('error')}")
    else:
        logger.info(f"Successfully retrieved page: {page_id}")

    return result


# ********************Fetch with recursive children support***************


def _fetch_block_children_recursive(
    oauth_token: str, block_id: str, max_depth: int = 3, current_depth: int = 0
) -> list:
    if current_depth >= max_depth:
        logger.warning(
            f"Max recursion depth ({max_depth}) reached for block {block_id}"
        )
        return []

    all_blocks = []
    start_cursor = None

    while True:
        params = {"page_size": 100}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = make_notion_request(
            "GET", f"/v1/blocks/{block_id}/children", oauth_token, params=params
        )

        if "error" in response:
            logger.error(
                f"Failed to fetch children for block {block_id}: {response.get('error')}"
            )
            break

        blocks = response.get("results", [])

        for block in blocks:
            if block.get("has_children", False):
                block_type = block.get("type")
                logger.info(
                    f"Fetching nested children for {block_type} block {block['id']}"
                )
                nested_children = _fetch_block_children_recursive(
                    oauth_token, block["id"], max_depth, current_depth + 1
                )
                block["children"] = nested_children

        all_blocks.extend(blocks)

        if not response.get("has_more", False):
            break

        start_cursor = response.get("next_cursor")

    return all_blocks


def _extract_title(page_data: dict) -> str:
    """Extract the title from page properties."""
    try:
        title_property = page_data.get("properties", {}).get("title", {})
        title_items = title_property.get("title", [])

        if title_items:
            return "".join(item.get("plain_text", "") for item in title_items)
        return ""
    except Exception:
        return ""


def _extract_plain_text(blocks: list) -> str:
    """Extract plain text content from Notion blocks recursively."""
    text_parts = []

    for block in blocks:
        block_type = block.get("type")

        if not block_type:
            continue

        block_content = block.get(block_type, {})
        rich_text = block_content.get("rich_text", [])

        for text_item in rich_text:
            plain_text = text_item.get("plain_text", "")
            if plain_text:
                text_parts.append(plain_text)

        if block.get("has_children"):
            # already-loaded children only
            children = block.get("children", [])
            if children:
                child_text = _extract_plain_text(children)
                if child_text:
                    text_parts.append(child_text)

    return "\n".join(text_parts)


def _simplify_page_response(page_data: dict) -> dict:
    return {
        "page_id": page_data.get("id"),
        "title": _extract_title(page_data),
        "content": _extract_plain_text(page_data.get("children", [])),
        "url": page_data.get("url"),
    }


############# Notion Fetch Service #############
def fetch_page_content_service(
    oauth_token: str,
    page_id: str,
    include_children: bool = True,
    recursive: bool = False,
    max_depth: int = 3,
    page_size: int = 100,
    start_cursor: Optional[str] = None,
) -> Dict:
    logger.info(
        f"[notion_fetch] page_id='{page_id}', include_children={include_children}, recursive={recursive}"
    )

    page_data = make_notion_request("GET", f"/v1/pages/{page_id}", oauth_token)

    if "error" in page_data:
        logger.error(f"Failed to fetch page: {page_id}: {page_data.get('error')}")
        return page_data

    if include_children:
        if recursive:
            logger.info(f"Fetching children recursively (max_depth={max_depth})")
            all_children = _fetch_block_children_recursive(
                oauth_token, page_id, max_depth=max_depth
            )
            page_data["children"] = all_children
            page_data["has_more_children"] = False
            page_data["next_cursor"] = None
            page_data["children_count"] = len(all_children)
        else:
            params = {"page_size": min(page_size, 100)}
            if start_cursor:
                params["start_cursor"] = start_cursor

            children_data = make_notion_request(
                "GET", f"/v1/blocks/{page_id}/children", oauth_token, params=params
            )

            if "error" not in children_data:
                page_data["children"] = children_data.get("results", [])
                page_data["has_more_children"] = children_data.get("has_more", False)
                page_data["next_cursor"] = children_data.get("next_cursor")
                logger.info(f"Retrieved {len(page_data['children'])} child blocks")
            else:
                logger.error(f"Failed to fetch children: {children_data.get('error')}")
                page_data["children_error"] = children_data.get("error")

    return _simplify_page_response(page_data)

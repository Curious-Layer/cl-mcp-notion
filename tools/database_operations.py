"""Database operation tools for Notion API"""

import logging
from typing import Dict, List, Optional

from utils import make_notion_request

logger = logging.getLogger("notion-mcp-server")


def get_database_service(oauth_token: str, database_id: str) -> Dict:
    logger.info(f"[get_database_service] database_id='{database_id}'")

    result = make_notion_request("GET", f"/v1/databases/{database_id}", oauth_token)

    if "error" in result:
        logger.error(
            f"Failed to retrieve database: {database_id}: {result.get('error')}"
        )
    else:
        logger.info(f"Successfully retrieved database: {database_id}")
        logger.info(
            f"Database has {len(result.get('data_sources', []))} data source(s)"
        )

    return result


def get_data_source_service(oauth_token: str, data_source_id: str) -> Dict:
    logger.info(f"[get_data_source_service] data_source_id='{data_source_id}'")

    result = make_notion_request(
        "GET", f"/v1/data_sources/{data_source_id}", oauth_token
    )

    if "error" in result:
        logger.error(
            f"Failed to retrieve data source: {data_source_id}: {result.get('error')}"
        )
    else:
        logger.info(f"Successfully retrieved data source: {data_source_id}")
        logger.info(f"Properties: {list(result.get('properties', {}).keys())}")

    return result


def query_data_source_service(
    oauth_token: str,
    data_source_id: str,
    filter: Optional[Dict] = None,
    sorts: Optional[List[Dict]] = None,
    page_size: int = 100,
    start_cursor: Optional[str] = None,
) -> Dict:
    logger.info(f"[query_data_source_service] data_source_id='{data_source_id}'")

    body = {"page_size": min(page_size, 100)}

    if filter:
        body["filter"] = filter
        logger.info(f"Applying filter: {filter.get('property', 'compound filter')}")

    if sorts:
        body["sorts"] = sorts
        logger.info(f"Applying {len(sorts)} sort(s)")

    if start_cursor:
        body["start_cursor"] = start_cursor

    result = make_notion_request(
        "POST", f"/v1/data_sources/{data_source_id}/query", oauth_token, body=body
    )

    if "error" in result:
        logger.error(f"Failed to query data source: {result.get('error')}")
    else:
        results_count = len(result.get("results", []))
        has_more = result.get("has_more", False)
        logger.info(f"Query returned {results_count} page(s), has_more={has_more}")

    return result


def create_database_service(
    oauth_token: str,
    parent_id: str,
    parent_type: str = "page_id",
    title: str = "Untitled Database",
    properties: Optional[Dict] = None,
    data_source_title: Optional[str] = None,
    is_inline: bool = False,
    icon: Optional[Dict] = None,
    cover: Optional[Dict] = None,
) -> Dict:
    logger.info(f"[create_database_service] parent_id={parent_id}, title={title}")

    if parent_type != "page_id":
        logger.error(f"Invalid parent_type: {parent_type}")
        return {"error": "parent_type must be 'page_id' for databases"}

    if not properties:
        properties = {"Name": {"title": {}}}

    body = {
        "parent": {"type": parent_type, parent_type: parent_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "initial_data_source": {"properties": properties},
        "is_inline": is_inline,
    }

    if data_source_title:
        body["initial_data_source"]["title"] = [
            {"type": "text", "text": {"content": data_source_title}}
        ]
        logger.info(f"Setting data source title: {data_source_title}")

    if icon:
        body["icon"] = icon
        logger.info(f"Setting icon: type={icon.get('type')}")

    if cover:
        body["cover"] = cover
        logger.info(f"Setting cover: type={cover.get('type')}")

    result = make_notion_request("POST", "/v1/databases", oauth_token, body=body)

    if "error" in result:
        logger.error(f"Failed to create database: {result.get('error')}")
    else:
        logger.info(f"Successfully created database: {result.get('id')}")

    return result

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

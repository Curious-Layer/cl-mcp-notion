"""Upstream API client for MewCP Notion MCP Server."""

import logging
from typing import Any

import requests
from fastmcp_credentials import get_credentials

from .config import NOTION_API_BASE, NOTION_VERSION, CONNECT_TIMEOUT, READ_TIMEOUT

logger = logging.getLogger("notion-mcp.service")


def _get_access_token() -> str:
    cred = get_credentials()
    if not cred.access_token:
        raise ValueError("Credential must have access_token")
    return cred.access_token


def _auth_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_access_token()}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _parse_retry_after(header: str | None) -> int | None:
    if not header:
        return None
    try:
        return int(header)
    except ValueError:
        return None


def notion_request(
    method: str,
    endpoint: str,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: tuple[int, int] | None = None,
) -> tuple[dict[str, Any], int, int | None]:
    """Make a Notion API request.

    Returns (response_dict, status_code, retry_after_seconds).
    """
    if timeout is None:
        timeout = (CONNECT_TIMEOUT, READ_TIMEOUT)
    url = f"{NOTION_API_BASE}{endpoint}"
    resp = requests.request(
        method=method,
        url=url,
        headers=_auth_headers(),
        json=body,
        params=params,
        timeout=timeout,
    )
    try:
        data = resp.json()
    except Exception:
        data = {"error": resp.text or "Empty response body"}

    retry_after_hdr = resp.headers.get("Retry-After")
    return data, resp.status_code, _parse_retry_after(retry_after_hdr)

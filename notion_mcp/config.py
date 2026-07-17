"""Configuration for MewCP Notion MCP Server."""

import logging
import os

from pythonjsonlogger import jsonlogger

# First versioned release of the restructured server — no prior packaged
# version existed, so this starts at v1.0.0 rather than a major bump.
SERVER_VERSION = "v1.0.0"

# List breaking changes introduced in this version. Empty for non-breaking releases.
# Each entry: {"tool": str, "change": str, "migration": str}
# The gateway reads this on new server registration to auto-notify affected workflow owners.
BREAKING_CHANGES: list[dict] = []

NOTION_API_BASE = "https://api.notion.com"
NOTION_VERSION = "2025-09-03"  # Notion-Version header value — preserved from the legacy client

# This server calls the Notion REST API directly with `requests` (no SDK manages
# transport), so timeouts belong here. The legacy client made requests.request()
# calls with no timeout at all — a hung upstream connection could block forever.
CONNECT_TIMEOUT = 5   # TCP connection — fixed across all servers
READ_TIMEOUT = 30     # Notion REST endpoints are synchronous request/response; 30s covers normal latency


def configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler()
    handler.setFormatter(
        jsonlogger.JsonFormatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")
    )
    logging.basicConfig(level=level, handlers=[handler], force=True)

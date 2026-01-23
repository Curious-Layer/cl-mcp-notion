"""
MCP server for Notion API
It will Provide acces to Notion API's via MCP

"""

from venv import logger
from fastmcp import FastMCP
from notion_client import Client
from typing import Dict
import json
import argparse

mcp = FastMCP("CL Notion MCP Server")


def _get_notion_data(token: str) -> Dict:
    try:
        token_data = json.loads(token)
        auth_data = {
            "access_token": token_data.get("access_token") or token_data.get("token"),
            "token_type": token_data.get("token_type", "bearer"),
            "bot_id": token_data.get("bot_id"),
            "workspace_id": token_data.get("workspace_id"),
            "workspace_name": token_data.get("workspace_name"),
        }

        return auth_data
    except Exception as e:
        return f"Error parsing token data: {str(e)}"


def _get_client(oauth_token: str):
    auth_data = _get_notion_data(oauth_token)
    access_token = auth_data.get("access_token")

    if not access_token:
        raise ValueError("Invalid OAuth token provided.")

    client = Client(auth=access_token)

    return client


# mcp tools


@mcp.tool(
    name="get_current_user",
    description="Get information about the authenticated bot user",
)
def get_current_user(oauth_token: str) -> Dict:
    """Get current bot user information"""

    try:
        client = _get_client(oauth_token)
        response = client.users.me()

        return response
    except Exception as e:
        return {"error": str(e)}


# parse cmd line args


def parse_args():
    parser = argparse.ArgumentParser(description="Notion MCP Server")
    parser.add_argument(
        "-t",
        "--transport",
        help="Transport method for MCP (Allowed Values: 'stdio', 'sse', or 'streamable-http')",
        default=None,
    )
    parser.add_argument("--host", help="Host to bind the server to", default=None)
    parser.add_argument(
        "--port", type=int, help="Port to bind the server to", default=None
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Build kwargs for mcp.run() only with provided values
    run_kwargs = {}
    if args.transport:
        run_kwargs["transport"] = args.transport

    if args.host:
        run_kwargs["host"] = args.host
        logger.info(f"Host: {args.host}")
    if args.port:
        run_kwargs["port"] = args.port

    try:
        # Start the MCP server
        mcp.run(**run_kwargs)

    except Exception as e:
        raise

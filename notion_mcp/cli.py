"""CLI argument parsing for MewCP Notion MCP Server."""

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Notion MCP Server")
    parser.add_argument(
        "-t",
        "--transport",
        help="Transport method: 'stdio', 'sse', or 'streamable-http'",
        default="streamable-http",
    )
    parser.add_argument("--host", help="Host to bind to", default="0.0.0.0")
    parser.add_argument("--port", type=int, help="Port to bind to", default=8000)
    return parser.parse_args()

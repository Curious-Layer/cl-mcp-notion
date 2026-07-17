from fastmcp import FastMCP

from .pages_read_tools import register_pages_read_tools
from .pages_write_tools import register_pages_write_tools
from .databases_tools import register_databases_tools
from .users_tools import register_users_tools


def register_tools(mcp: FastMCP) -> None:
    register_pages_read_tools(mcp)
    register_pages_write_tools(mcp)
    register_databases_tools(mcp)
    register_users_tools(mcp)

# Notion MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Notion API endpoints with OAuth authentication.

## Features

This MCP server provides the following Notion operations:

### Search & Read Operations

- **search_notion**: Search all pages and databases by title or list all pages
- **get_page**: Retrieve a Notion page by ID with properties and metadata
- **fetch_page_content**: Retrieve a page with full content including all child blocks (supports recursive fetching)

### Page Management

- **create_page_under_page**: Create a new page under a parent page
- **create_workspace_page**: Create a new page at workspace level (no parent)
- **update_page**: Update an existing page's properties, icon, cover, and metadata
- **append_text_block**: Append various text blocks (paragraphs, headings, lists, etc.) to a page

### Database Operations(Not Fully Supported)

- **get_database**: Retrieve a database object by ID with title, parent, and data sources
- **get_data_source**: Retrieve a database schema/properties by ID
- **query_data_source**: Query a database with filtering and sorting
- **create_database**: Create a new database as a child of an existing page

### User Operations

- **list_users**: List all users in the workspace (guests not included)
- **get_user**: Retrieve a specific user by their ID
- **get_self**: Retrieve the bot user associated with your API token

## Setup

### 1. Install Dependencies

Using pip:

```bash
pip install -r requirements.txt
```

### 2. Configure Notion OAuth

You need to create a Notion integration with OAuth support:

1. Go to [Notion Developers](https://www.notion.so/my-integrations)
2. Create a new integration
3. Configure OAuth settings:
   - Add redirect URI: `http://localhost:8080` or your client URL
   - Note your Client ID and Client Secret
4. Set required capabilities:
   - Read content
   - Update content
   - Insert content
   - Read user information

### 4. Configure Your MCP Client

#### For Claude Desktop (stdio mode - default)

Add this to your Claude Desktop MCP settings file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "notion": {
      "command": "python",
      "args": [
        "D:\\Code\\Curious Layer\\notion_mcp_server\\server.py"
      ],
      "cwd": "D:\\Code\\Curious Layer\\notion_mcp_server"
    }
  }
}
```

#### For HTTP/SSE Transport

You can run the server with different transport modes:

**Streamable HTTP** (default):

```bash
python server.py --transport streamable-http --host 0.0.0.0 --port 8080
```

**stdio**:

```bash
python server.py --transport stdio
```

## Usage Examples

### Search Pages

```json
{
  "tool": "search_notion",
  "arguments": {
    "oauth_token": "your_oauth_token",
    "query": "meeting notes",
    "filter_type": "page",
    "page_size": 10
  }
}
```

### Create a New Page

```json
{
  "tool": "create_page_under_page",
  "arguments": {
    "oauth_token": "your_oauth_token",
    "parent_page_id": "parent-page-id",
    "title": "My New Page",
    "position": { "type": "page_end" }
  }
}
```

### Fetch Page Content

```json
{
  "tool": "fetch_page_content",
  "arguments": {
    "oauth_token": "your_oauth_token",
    "page_id": "page-id",
    "include_children": true,
    "recursive": true,
    "max_depth": 3
  }
}
```

### Append Text Block

```json
{
  "tool": "append_text_block",
  "arguments": {
    "oauth_token": "your_oauth_token",
    "block_id": "page-id",
    "type": "paragraph",
    "content": "This is a new paragraph",
    "color": "blue",
    "position": "end"
  }
}
```

### Update Page

```json
{
  "tool": "update_page",
  "arguments": {
    "oauth_token": "your_oauth_token",
    "page_id": "page-id",
    "properties": {
      "title": {
        "title": [
          {
            "text": {
              "content": "Updated Title"
            }
          }
        ]
      }
    },
    "archived": false
  }
}
```

### Query Database

```json
{
  "tool": "query_data_source",
  "arguments": {
    "oauth_token": "your_oauth_token",
    "data_source_id": "database-id",
    "filter": {
      "property": "Status",
      "status": {
        "equals": "In Progress"
      }
    },
    "sorts": [
      {
        "property": "Created",
        "direction": "descending"
      }
    ]
  }
}
```

### Create Database

```json
{
  "tool": "create_database",
  "arguments": {
    "oauth_token": "your_oauth_token",
    "parent_id": "parent-page-id",
    "title": "My Database",
    "properties": {
      "Name": {
        "title": {}
      },
      "Status": {
        "select": {
          "options": [
            { "name": "To Do" },
            { "name": "In Progress" },
            { "name": "Done" }
          ]
        }
      }
    }
  }
}
```

## API Parameters

### Text Block Types

- `paragraph` - Regular paragraph text
- `heading_1` - Heading level 1
- `heading_2` - Heading level 2
- `heading_3` - Heading level 3
- `bulleted_list_item` - Bulleted list item
- `numbered_list_item` - Numbered list item
- `to_do` - Todo/checkbox item
- `toggle` - Toggle/collapsible block
- `quote` - Quote block
- `callout` - Callout/alert block

### Available Colors

- `default`, `gray`, `brown`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `red`
- Background colors: Add `_background` suffix (e.g., `blue_background`)

### Filter Types

- `page` - Filter for pages only
- `data_source` - Filter for databases only

### Position Options

- `page_end` / `end` - Insert at the end
- `page_start` / `start` - Insert at the beginning

## Deployment

### Railway Deployment

This server is configured for Railway deployment with `railway.json`:

```bash
# Deploy to Railway
railway up
```

The server will run on port 8080 using streamable-http transport.

### Environment Variables

For production deployment, set:

- `NOTION_CLIENT_ID` - Your Notion OAuth client ID
- `NOTION_CLIENT_SECRET` - Your Notion OAuth client secret

## Troubleshooting

### Permission Denied

Ensure your Notion integration has the required capabilities:

1. Go to [Notion My Integrations](https://www.notion.so/my-integrations)
2. Select your integration to public
3. Verify all required capabilities are enabled
4. Share pages/databases with your integration

### Rate Limiting

Notion API has rate limits. If you experience rate limit errors (HTTP 429):

- Reduce `page_size` parameters
- Add delays between bulk operations
- Check Notion API status page

### Connection Issues

If the server fails to start:

1. Check if the port is already in use
2. Verify Python version (3.12+ recommended)
3. Ensure all dependencies are installed
4. Check firewall settings for HTTP transport

## Security Notes

- **Never commit OAuth tokens** to version control
- Keep your `NOTION_CLIENT_SECRET` secure
- The server is stateless - each request requires an `oauth_token`
- OAuth tokens expire and need to be refreshed periodically
- Use HTTPS in production environments

## Logging

The server logs all operations with timestamps:

- `INFO`: Normal operations and API calls
- `WARNING`: Rate limits and warnings
- `ERROR`: API failures and authentication issues

Logs include:

- Request type and parameters
- Response status
- Error details with stack traces

## Architecture

This is a **stateless server** that:

- Does not store OAuth tokens
- Requires `oauth_token` parameter in every request
- Supports multi-user scenarios
- Is horizontally scalable

### Project Structure

```
notion_mcp_server/
├── tools/
│   ├── __init__.py
│   ├── read_operations.py      # Search, get, fetch operations
│   └── write_operations.py     # Create, update, append operations
    |__ user_operations.py      # User-related operations
    |__ database_operations.py  # Database-related operations
├── utils/
│   └── notion_utils.py         # HTTP request utilities
├── notion_mcp_server.py        # Main server file
├── requirements.txt            # Python dependencies
└── railway.json                # Railway deployment config
```

## Resources

- [Notion API Documentation](https://developers.notion.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

**Your Notion workspace, fully accessible through AI.**

A Model Context Protocol (MCP) server that exposes Notion's API for managing pages, databases, blocks, and users across your workspace.


## Overview

The Notion MCP Server provides a complete interface to your Notion workspace:

- Search, read, and write pages with full block-level content control
- Create and query databases (data sources) with filters, sorts, and pagination
- Manage workspace users and retrieve bot/workspace identity

Perfect for:

- AI assistants that need to read or update Notion pages and databases
- Automating content creation, knowledge base updates, and task management
- Building tools that integrate Notion with other services


## Tools

### Pages — Read

<details>
<summary><code>search_notion</code> — Search pages and databases by title</summary>

Search all pages and databases by title or list all pages

**Inputs:**
```
- `query` (string, optional, default: "") — Search query string, keep it empty to list all pages
- `filter_type` (string, optional) — Filter by 'page' or 'data_source'.
- `page_size` (int, optional, default: 20) — Number of pages to return (max 100)
- `start_cursor` (string, optional) — Cursor from a previous response to page through results.
```

**Output `data` schema:**

```typescript
{
  pages: {
    id: string | null;
    title: string;
    url: string | null;
    last_edited_time: string | null;
  }[];
  has_more: boolean;
  next_cursor: string | null;
}
```

</details>


<details>
<summary><code>get_page</code> — Retrieve a page by ID</summary>

Retrieve a Notion page by ID with properties and metadata

**Inputs:**
```
- `page_id` (string, required) — Notion page ID (UUID) to retrieve.
```

**Output `data` schema:**

```typescript
{
  id: string | null;
  object: string | null;
  url: string | null;
  public_url: string | null;
  created_time: string | null;
  last_edited_time: string | null;
  archived: boolean | null;
  in_trash: boolean | null;
  parent: object | null;
  properties: object | null;
  icon: object | null;
  cover: object | null;
}
```

</details>


<details>
<summary><code>fetch_page_content</code> — Retrieve a page with full block content</summary>

Retrieve a Notion page with its full content including all child blocks and properties

**Inputs:**
```
- `page_id` (string, required) — Notion page ID (UUID) to fetch content for.
- `include_children` (bool, optional, default: true) — Whether to fetch and include the page's child blocks.
- `recursive` (bool, optional, default: false) — Recursively fetch nested children of child blocks, up to max_depth.
- `max_depth` (int, optional, default: 3) — Maximum recursion depth when recursive=True.
- `page_size` (int, optional, default: 100) — Number of child blocks to fetch per page when recursive=False (max 100).
- `start_cursor` (string, optional) — Cursor from a previous response to page through child blocks (non-recursive only).
```

**Output `data` schema:**

```typescript
{
  page_id: string | null;
  title: string;
  content: string;
  url: string | null;
  has_more_children: boolean | null;
  next_cursor: string | null;
  children_count: number | null;
}
```

</details>


### Pages — Write

<details>
<summary><code>create_page_under_page</code> — Create a new page under a parent page</summary>

Create a new page under a parent page

**Inputs:**
```
- `parent_page_id` (string, required) — The ID of the parent page this new page will be created under.
- `title` (string, optional, default: "Untitled New page Created") — The title for the new page. Defaults to 'Untitled New page Created' if omitted.
- `position` (object, optional) — Insert postion. strict Format:{"type": "page_end"} or {"type": "page_start"}
```

**Output `data` schema:**

```typescript
{
  id: string | null;
  object: string | null;
  url: string | null;
  public_url: string | null;
  created_time: string | null;
  last_edited_time: string | null;
  archived: boolean | null;
  in_trash: boolean | null;
  parent: object | null;
  properties: object | null;
  icon: object | null;
  cover: object | null;
}
```

</details>


<details>
<summary><code>create_workspace_page</code> — Create a top-level workspace page</summary>

Create a new page at a workspace level (without parent page)

**Inputs:**
```
- `title` (string, optional, default: "Untitled New page Created") — The title for the new page. Defaults to 'Untitled New page Created' if omitted.
```

**Output `data` schema:**

```typescript
{
  id: string | null;
  object: string | null;
  url: string | null;
  public_url: string | null;
  created_time: string | null;
  last_edited_time: string | null;
  archived: boolean | null;
  in_trash: boolean | null;
  parent: object | null;
  properties: object | null;
  icon: object | null;
  cover: object | null;
}
```

</details>


<details>
<summary><code>update_page</code> — Update a page's properties and metadata</summary>

Update an existing Notion page's properties and metadata. Providing `properties`, `icon`, `cover`, or other fields replaces the corresponding current values rather than merging with them — the original state is not stored by the API after the call. Call get_page first to see current property values before updating. The response includes both the before and after state so you have a full record of what changed.

**Inputs:**
```
- `page_id` (string, required) — The ID of the Notion page to update.
- `properties` (object, optional) — A dict of Notion page property updates keyed by property name; replaces the corresponding existing property values rather than merging with them. Omit to leave properties unchanged.
- `icon` (object, optional) — A Notion file, emoji, or external object to set as the page icon. Omit to leave the icon unchanged.
- `cover` (object, optional) — A Notion file or external object to set as the page cover image. Omit to leave the cover unchanged.
- `archived` (bool, optional) — Whether to archive (true) or restore (false) the page. Omit to leave archival state unchanged.
- `in_trash` (bool, optional) — Whether to move the page to (true) or restore it from (false) the trash. Omit to leave trash state unchanged.
- `is_locked` (bool, optional) — Whether to lock (true) or unlock (false) the page to prevent further edits. Omit to leave the lock state unchanged.
- `template` (object, optional) — A Notion page template object to reapply to the page. Omit to leave the current template unchanged.
- `erase_content` (bool, optional) — Whether to clear the page's existing block content before applying the update. Omit to leave existing content in place.
```

**Output `data` schema:**

```typescript
{
  before: {
    id: string | null;
    object: string | null;
    url: string | null;
    public_url: string | null;
    created_time: string | null;
    last_edited_time: string | null;
    archived: boolean | null;
    in_trash: boolean | null;
    parent: object | null;
    properties: object | null;
    icon: object | null;
    cover: object | null;
  };
  after: {
    id: string | null;
    object: string | null;
    url: string | null;
    public_url: string | null;
    created_time: string | null;
    last_edited_time: string | null;
    archived: boolean | null;
    in_trash: boolean | null;
    parent: object | null;
    properties: object | null;
    icon: object | null;
    cover: object | null;
  };
}
```

</details>


<details>
<summary><code>append_text_block</code> — Append a text block to a page</summary>

Append a text block to a page

**Inputs:**
```
- `block_id` (string, required) — The ID could be page ID or parent block ID
- `type` (string, required, one of: paragraph | heading_1 | heading_2 | heading_3 | bulleted_list_item | numbered_list_item | to_do | toggle | quote | callout) — The type of text block to create
- `content` (string, required) — The text content for the block
- `checked` (bool, optional) — For to_do blocks only - whether the item is checked
- `color` (string, optional) — text color or background color. available colors : [ 'default', 'gray', 'brown', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'red'] background color format : eg. red_background or blue_background
- `position` (string, optional, one of: end | start) — Position to insert the new block;
```

**Output `data` schema:**

```typescript
{
  blocks: {
    id: string | null;
    type: string | null;
    created_time: string | null;
  }[];
}
```

</details>


### Databases

<details>
<summary><code>get_database</code> — Retrieve a database by ID</summary>

Retrieve a database object by ID with title, parent, and data sources

**Inputs:**
```
- `database_id` (string, required) — The ID of the database to retrieve
```

**Output `data` schema:**

```typescript
{
  id: string | null;
  title: object[] | null;
  parent: object | null;
  data_sources: object[] | null;
  url: string | null;
  archived: boolean | null;
  created_time: string | null;
  last_edited_time: string | null;
  icon: object | null;
  cover: object | null;
}
```

</details>


<details>
<summary><code>get_data_source</code> — Retrieve a data source schema</summary>

Retrieve a data source (database schema/properties) by ID

**Inputs:**
```
- `data_source_id` (string, required) — The ID of the data source to retrieve
```

**Output `data` schema:**

```typescript
{
  id: string | null;
  properties: object | null;
  parent: object | null;
}
```

</details>


<details>
<summary><code>query_data_source</code> — Query a data source with filters and sorts</summary>

Query a data source to get pages with optional filtering and sorting

**Inputs:**
```
- `data_source_id` (string, required) — The ID of the data source to query
- `filter` (object, optional) — Notion filter object to restrict which pages are returned
- `sorts` (list, optional) — List of Notion sort objects controlling result order
- `page_size` (int, optional, default: 100) — Maximum number of results per page (silently capped at 100)
- `start_cursor` (string, optional) — Cursor from a previous response's next_cursor to page through results
```

**Output `data` schema:**

```typescript
{
  results: object[];
  has_more: boolean;
  next_cursor: string | null;
}
```

</details>


<details>
<summary><code>create_database</code> — Create a new database</summary>

Create a new database as a child of an existing page

**Inputs:**
```
- `parent_id` (string, required) — The ID of the parent page to create the database under
- `title` (string, optional, default: "Untitled Database") — Title of the new database
- `description` (string, optional) — Plain-text description of the database
- `properties` (object, optional) — Database schema properties keyed by column name (defaults to a single 'Name' title property)
- `is_inline` (bool, optional, default: false) — Whether the database should render inline within its parent page
- `icon` (object, optional) — Icon object to set on the database
- `cover` (object, optional) — Cover object to set on the database
```

**Output `data` schema:**

```typescript
{
  id: string | null;
  title: object[] | null;
  parent: object | null;
  data_sources: object[] | null;
  url: string | null;
  archived: boolean | null;
  created_time: string | null;
  last_edited_time: string | null;
  icon: object | null;
  cover: object | null;
}
```

</details>


### Users

<details>
<summary><code>list_users</code> — List workspace users</summary>

List all users in the workspace (guests not included)

**Inputs:**
```
- `page_size` (int, optional, default: 100) — Maximum number of users to return per page (values above 100 are clamped).
- `start_cursor` (string, optional) — Cursor from a previous response's next_cursor, used to page through results.
```

**Output `data` schema:**

```typescript
{
  results: {
    id: string | null;
    name: string | null;
    avatar_url: string | null;
    type: string | null;
    person: object | null;
    bot: object | null;
  }[];
  has_more: boolean;
  next_cursor: string | null;
}
```

</details>


<details>
<summary><code>get_user</code> — Retrieve a specific user</summary>

Retrieve a specific user by their ID

**Inputs:**
```
- `user_id` (string, required) — ID of the user to retrieve.
```

**Output `data` schema:**

```typescript
{
  id: string | null;
  name: string | null;
  avatar_url: string | null;
  type: string | null;
  person: object | null;
  bot: object | null;
}
```

</details>


<details>
<summary><code>get_self</code> — Retrieve the bot user for your token</summary>

Retrieve the bot user associated with your API token, including owner and workspace info

**Inputs:**
```
None
```

**Output `data` schema:**

```typescript
{
  id: string | null;
  name: string | null;
  avatar_url: string | null;
  type: string | null;
  person: object | null;
  bot: object | null;
  owner: object | null;
  workspace_name: string | null;
  workspace_limits: object | null;
}
```

</details>


## API Parameters Reference

<details>
<summary><strong>Response Envelope</strong></summary>

Every tool returns the same top-level envelope. Only `data` varies per tool.

```json
// Success
{
  "success": true,
  "statusCode": 200,
  "retriable": false,
  "retry_after_seconds": null,
  "error": null,
  "data": { ... }
}

// Error
{
  "success": false,
  "statusCode": 400,
  "retriable": false,
  "retry_after_seconds": null,
  "error": { "code": "VALIDATION_ERROR", "message": "At least one update parameter must be provided", "details": {} },
  "data": null
}
```

- `retriable` — `true` when it is safe to retry (rate limit, network error, 503). `false` for validation and auth errors.
- `retry_after_seconds` — seconds to wait before retrying; present only when `retriable` is `true` and the upstream specifies a delay.
- `error.code` — machine-readable string: `VALIDATION_ERROR`, `AUTH_ERROR`, `UPSTREAM_ERROR`, `SERVER_ERROR`.

</details>

<details>
<summary><strong>Common Parameters</strong></summary>

- `page_size` — Maximum number of results per page. Accepted by `search_notion`, `fetch_page_content`, `query_data_source`, and `list_users`; each tool silently caps it at 100.
- `start_cursor` — Cursor value from a previous response's `next_cursor` field, used to page through results. Omit for the first page.
- `filter` — Restricts which results are returned. Shape differs by tool: `search_notion` takes `filter_type` ('page' or 'data_source'), while `query_data_source` takes a full Notion filter object.

</details>

<details>
<summary><strong>Resource Formats</strong></summary>

**Notion ID:**

```
UUID, dashes optional
Example: 8f9b3c2d-1a2b-3c4d-5e6f-7a8b9c0d1e2f
```

**Block Types (`append_text_block`):**

```
paragraph | heading_1 | heading_2 | heading_3 | bulleted_list_item | numbered_list_item | to_do | toggle | quote | callout
```

**Colors (`append_text_block`):**

```
default | gray | brown | orange | yellow | green | blue | purple | pink | red
Background variant: append "_background", e.g. red_background, blue_background
```

</details>


## Troubleshooting

<details>
<summary><strong>Missing or Invalid Headers</strong></summary>

- **Cause:** OAuth access token not provided in request headers or incorrect format
- **Solution:**
  1. Verify `Authorization: Bearer YOUR_ACCESS_TOKEN` and `X-Mewcp-Credential-Id: CREDENTIAL-ID` headers are present
  2. Check the OAuth token has not expired — reconnect your Notion account in your MewCP account if needed

</details>

<details>
<summary><strong>Insufficient Credits</strong></summary>

- **Cause:** API calls have exceeded your request limits
- **Solution:**
  1. Check credit usage in your Curious Layer dashboard
  2. Upgrade to a paid plan or add credits for higher limits
  3. Contact support for credit adjustments

</details>

<details>
<summary><strong>Credential Not Connected</strong></summary>

- **Cause:** No Notion credential linked to your account
- **Solution:**
  1. Go to **Credentials** in your MewCP dashboard
  2. Connect your Notion account (OAuth)
  3. Retry the request with the correct `X-Mewcp-Credential-Id` header

</details>

<details>
<summary><strong>Malformed Request Payload</strong></summary>

- **Cause:** JSON payload is invalid or missing required fields
- **Solution:**
  1. Validate JSON syntax before sending
  2. Ensure all required tool parameters are included
  3. Check parameter types match expected values (e.g. `filter` and `sorts` must match Notion's expected object schema)

</details>

<details>
<summary><strong>Server Not Found</strong></summary>

- **Cause:** Incorrect server name in the API endpoint
- **Solution:**
  1. Verify endpoint format: `{server-name}/mcp/{tool-name}`
  2. Use correct server name from documentation
  3. Check available servers in your Curious Layer account

</details>

<details>
<summary><strong>Notion API Error</strong></summary>

- **Cause:** Upstream Notion API returned an error
- **Solution:**
  1. Check Notion service status at [Notion Status Page](https://status.notion.so)
  2. Verify your integration has access to the target page or database (share it with the integration in Notion)
  3. Review the error message for specific details

</details>

---

<details>
<summary><strong>Resources</strong></summary>

- **[Notion API Documentation](https://developers.notion.com)** — Official API reference
- **[Notion API Reference](https://developers.notion.com/reference)** — Complete endpoint reference
- **[FastMCP Docs](https://gofastmcp.com/v2/getting-started/welcome)** — FastMCP specification
- **[FastMCP Credentials](https://pypi.org/project/fastmcp-credentials/)** — FastMCP Credentials package for credential handling


</details>

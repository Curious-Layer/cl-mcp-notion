# Notion MCP Server - Tool Implementation Plan

Core API endpoints to implement as MCP tools:

## Read Operations

| Tool Name            | Endpoint                            | Method | Description                                |
| -------------------- | ----------------------------------- | ------ | ------------------------------------------ |
| `get_database`       | `/v1/databases/{database_id}`       | `GET`  | Get database schema and properties         |
| `query_database`     | `/v1/databases/{database_id}/query` | `POST` | Query database with filters and sorts      |
| `get_block_children` | `/v1/blocks/{block_id}/children`    | `GET`  | Get child blocks (content) of a page/block |
| `get_comments`       | `/v1/comments`                      | `GET`  | Get comments on a page or block            |
| `get_users` ✓        | `/v1/users`                         | `GET`  | List users in workspace                    |
| `get_user` ✓         | `/v1/users/{user_id}`               | `GET`  | Get specific user details                  |

## Write Operations

| Tool Name               | Endpoint                           | Method   | Description                                       |
| ----------------------- | ---------------------------------- | -------- | ------------------------------------------------- |
| `append_block_children` | `/v1/blocks/{block_id}/children`   | `PATCH`  | Add content blocks to a page                      |
| `update_block`          | `/v1/blocks/{block_id}`            | `PATCH`  | Update an existing block                          |
| `delete_block`          | `/v1/blocks/{block_id}`            | `DELETE` | Delete a block                                    |
| `create_comment`        | `/v1/comments`                     | `POST`   | Add a comment to a page or block                  |
| `notion_duplicate_page` | NA (need ot use diff. combination) | `POST`   | Duplicate a page from exihisting page or template |

## Database Operations

| Tool Name         | Endpoint                      | Method  | Description                           |
| ----------------- | ----------------------------- | ------- | ------------------------------------- |
| `create_database` | `/v1/databases`               | `POST`  | Create a new database                 |
| `update_database` | `/v1/databases/{database_id}` | `PATCH` | Update database properties and schema |

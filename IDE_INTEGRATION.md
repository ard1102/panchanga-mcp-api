# IDE Integration Guide

You can integrate this MCP server with various IDEs and AI tools.

## 1. Remote Integration (No Local Install) - Recommended for Cursor

If you have deployed the server (e.g., to Coolify) and have an API Key, you can connect directly without installing Python or dependencies locally.

### Cursor / VS Code (via SSE)

Cursor and some VS Code extensions support connecting to MCP servers via **SSE (Server-Sent Events)** URLs.

1.  Open **Cursor Settings** > **Features** > **MCP** (or similar menu).
2.  Add a new MCP Server:
    *   **Type**: SSE
    *   **URL**: `https://panchang-mcp.visionpair.cloud/sse?api_key=YOUR_API_KEY_HERE`
    
    *(Replace `YOUR_API_KEY_HERE` with your actual API Key)*

**Note**: We use the `?api_key=` query parameter because many current IDE UIs do not yet allow setting custom headers for MCP connections.

---

## 2. Claude Desktop (Local Install Required)

Currently, **Claude Desktop** primarily supports running local commands (`stdio`). It does not natively support connecting to a remote SSE URL without a local "bridge" script.

To use this with Claude Desktop, you must run the server code locally on your machine.

1.  **Install Python 3.12+**.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Edit Configuration**:
    -   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
    -   **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

    Add this config (update the path):

    ```json
    {
      "mcpServers": {
        "panchanga": {
          "command": "python",
          "args": [
            "C:/Path/To/Your/Project/panchanga-api/run_local.py"
          ],
          "env": {
            "PANCHANGAM_API_URL": "https://panchang.visionpair.cloud/api/panchanga"
          }
        }
      }
    }
    ```
    
    **Tip**: By setting `PANCHANGAM_API_URL` to your live backend (as shown above), you avoid needing to run the .NET backend locally!

4.  **Restart Claude Desktop**.

---

## 3. N8N Integration (Web)

See [N8N_INTEGRATION.md](N8N_INTEGRATION.md) for details on how to use the REST API endpoints in your workflows.

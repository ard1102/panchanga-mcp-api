# IDE Integration Guide

You can integrate this MCP server with various IDEs and AI tools.

## 1. Claude Desktop (Local)

To run the MCP server locally and connect it to Claude Desktop:

1.  Ensure you have **Python 3.12+** installed.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Edit your Claude Desktop configuration file:
    -   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
    -   **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

    Add the following configuration (update the path to your project):

    ```json
    {
      "mcpServers": {
        "panchanga": {
          "command": "python",
          "args": [
            "C:/Path/To/Your/Project/panchanga-api/run_local.py"
          ]
        }
      }
    }
    ```

4.  Restart Claude Desktop. You should see a generic "tool" icon indicating the server is connected.

---

## 2. Cursor (via SSE)

Cursor is adding support for MCP. Since you have a deployed SSE endpoint, you can try connecting via the "MCP" or "Model Context Protocol" settings if available in your version.

*   **URL**: `https://panchang-mcp.visionpair.cloud/sse`
*   **Transport**: SSE

*(Note: Cursor's MCP support is evolving rapidly; check their latest docs for specific configuration steps.)*

---

## 3. VS Code (via Extensions)

You can use extensions like "MCP Client" to connect to your server.

1.  **Local (Stdio)**: Point the extension to `run_local.py` (similar to Claude Desktop).
2.  **Remote (SSE)**: Configure the extension to connect to `https://panchang-mcp.visionpair.cloud/sse` with your API Key in the headers.

---

## 4. Windsurf / Other IDEs

Most MCP-compatible IDEs support the `stdio` method for local scripts. Follow the same pattern as Claude Desktop:
-   **Command**: `python`
-   **Args**: `["/absolute/path/to/run_local.py"]`

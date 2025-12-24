# n8n Integration Guide

You have three ways to use the Panchangam service in n8n.

## Option 1: Native MCP Integration (Recommended for AI Agents)

If you are using the **AI Agent** node in n8n (versions 1.70+), you can connect this tool directly as an MCP Tool.

### ⚠️ IMPORTANT: Authentication Requirement
You **MUST** use the **Header Auth** option.
**Do NOT** rely solely on the query parameter (`?api_key=...`) in the URL.
*   **Why?** The MCP protocol involves a "handshake" where the server tells the client a new URL to send messages to. This new URL *does not* include your original query parameters. If you don't use headers, the connection will break immediately after the handshake (Tool Discovery will fail).

### Configuration Steps
1.  Open your **AI Agent** node.
2.  Click **"Add Tool"** -> Select **"MCP Tool"**.
3.  **Create New Credentials**:
    *   **Type**: Select **"MCP Client (HTTP Streamable) API"**.
    *   **HTTP Streamable URL**: `https://panchang-mcp.visionpair.cloud/sse` (Do **NOT** add `?api_key=` here)
    *   **Authentication**: Select **Header Auth**.
    *   **Header Name**: `X-API-Key`
    *   **Header Value**: `YOUR_API_KEY_HERE`
        *(Replace `YOUR_API_KEY_HERE` with your actual key)*

4.  The AI Agent will now automatically see all available tools:
    *   `get_panchanga_data`
    *   `get_sankalpam_text`
    *   `get_sankalpam_audio`

### How it Works
1.  **Connection**: n8n connects to `/sse` (Authenticated via Header).
2.  **Discovery**: Server returns a new endpoint `/messages?session_id=...`.
3.  **Execution**: n8n posts to `/messages` (Authenticated via Header). 
    *If you missed the header, this step fails with 403 Forbidden.*

---

## Option 2: Secured HTTP API (Standard Workflows)

Use this if you are building a standard workflow (without AI Agent) or prefer manual control.

1.  Add an **HTTP Request** node.
2.  **Method**: `GET`
3.  **URL**: Choose one of the endpoints below.
4.  **Headers**: Add a header named `X-API-Key` with your secret key.
5.  **Query Parameters**: Add `latitude`, `longitude`, `timezone`, `locationName`.

### Endpoints
| Endpoint | Description |
| :--- | :--- |
| `/api/panchanga` | Returns accurate Tithi, Nakshatra, and other details. |
| `/api/sankalpam` | Returns the full Sankalpam text (Sanskrit/IAST). |
| `/api/voice` | Returns the audio file as a Base64 string (`audio_base64`). |

---

## Option 3: Legacy / Public API

*   **Base URL**: `https://panchang.visionpair.cloud/api/panchanga`
*   **Authentication**: None
*   **Features**: Basic Panchanga data only (No Voice, No High Precision).

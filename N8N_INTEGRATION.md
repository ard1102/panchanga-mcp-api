# n8n Integration Guide

You have three ways to use the Panchangam service in n8n.

## Option 1: Native MCP Integration (Recommended for AI Agents)

If you are using the **AI Agent** node in n8n (versions 1.70+), you can connect this tool directly as an MCP Tool.

1.  Open your **AI Agent** node.
2.  Click **"Add Tool"** -> Select **"MCP Tool"**.
3.  In the MCP Tool configuration:
    *   **Connection Type**: Select **"HTTP streamable"** (Note: In some versions this might be labeled "SSE", but "HTTP streamable" is the newer standard for MCP in n8n).
    *   **Server URL**: `https://panchang-mcp.visionpair.cloud/sse?api_key=YOUR_API_KEY_HERE`
    
    *(We use the `?api_key=` query parameter because n8n's MCP UI may not yet support custom headers).*

4.  The AI Agent will now automatically see all available tools:
    *   `get_panchanga_data`
    *   `get_sankalpam_text`
    *   `get_sankalpam_audio`

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

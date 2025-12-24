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

## Option 2: Add as "Workflow Tool" (Alternative to MCP)

If MCP integration is not available or failing, you can add the API as a **Workflow Tool**. This is the standard way to add custom capabilities to an AI Agent in n8n.

### Step 1: Create the "Panchanga Tool" Workflow
1.  Create a **New Workflow**.
2.  **Trigger**: Add an **"Execute Workflow Trigger"** node.
    *   Leave settings as default.
3.  **Action**: Add an **"HTTP Request"** node.
    *   **Method**: `GET`
    *   **URL**: `https://panchang-mcp.visionpair.cloud/api/panchanga`
    *   **Authentication**: Generic Credential Type -> **Header Auth**.
        *   **Name**: `X-API-Key`
        *   **Value**: `YOUR_API_KEY`
    *   **Query Parameters**:
        *   `latitude`: `{{ $json.latitude }}`
        *   `longitude`: `{{ $json.longitude }}`
        *   `timezone`: `{{ $json.timezone }}`
        *   `location_name`: `{{ $json.location_name }}` (Optional)
4.  **Output**: Add a **"Respond to Webhook"** node (or just ensure the HTTP Request is the last node).
    *   **Respond With**: JSON
    *   **Response Body**: `{{ $json }}` (The output of the HTTP Request)
5.  **Save** this workflow (e.g., name it "Tool - Get Panchanga").

### Step 2: Connect to AI Agent
1.  Go back to your **AI Agent** workflow.
2.  Add a **"Workflow Tool"** node.
3.  **Connect** it to the "Tools" input of the AI Agent node.
4.  **Configuration**:
    *   **Name**: `get_panchanga`
    *   **Description**: `Call this tool to get Hindu Panchanga details (Tithi, Nakshatra, Yoga) for a specific location and date.`
    *   **Workflow ID**: Select the "Tool - Get Panchanga" workflow you created in Step 1.
    *   **Schema** (JSON):
        ```json
        {
          "type": "object",
          "properties": {
            "latitude": { "type": "number", "description": "Latitude of the location" },
            "longitude": { "type": "number", "description": "Longitude of the location" },
            "timezone": { "type": "number", "description": "Timezone offset (e.g., 5.5 for IST)" },
            "location_name": { "type": "string", "description": "Name of the city/location" }
          },
          "required": ["latitude", "longitude", "timezone"]
        }
        ```

### Repeat for other tools
You can create similar "Tool Workflows" for `get_sankalpam_text` (`/api/sankalpam`) and `get_sankalpam_audio` (`/api/voice`).

---

## Option 3: Secured HTTP API (Standard Workflows)

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

## Option 4: Legacy / Public API

*   **Base URL**: `https://panchang.visionpair.cloud/api/panchanga`
*   **Authentication**: None
*   **Features**: Basic Panchanga data only (No Voice, No High Precision).

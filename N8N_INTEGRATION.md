# n8n Integration Guide

You have two main ways to use the Panchangam service in n8n.

## Option 1: Secured API (High Precision & Voice) - **RECOMMENDED**

Use this option if you want:
*   **High Precision Calculations** (using PyEphem)
*   **Audio/Voice Generation**
*   **Authentication** (Security)

### Configuration
*   **Base URL**: `https://panchang-mcp.visionpair.cloud`
*   **Authentication**: You **MUST** send your API Key in the headers.

### Steps in n8n
1.  Add an **HTTP Request** node.
2.  **Method**: `GET`
3.  **URL**: Choose one of the endpoints below.
4.  **Headers**: Add a header named `X-API-Key` with your secret key (set in Coolify).
5.  **Query Parameters**: Add `latitude`, `longitude`, `timezone`, `locationName`.

### Endpoints
| Endpoint | Description |
| :--- | :--- |
| `/api/panchanga` | Returns accurate Tithi, Nakshatra, and other details. |
| `/api/sankalpam` | Returns the full Sankalpam text (Sanskrit/IAST). |
| `/api/voice` | Returns the audio file as a Base64 string (`audio_base64`). |

---

## Option 2: Public API (Basic Data)

Use this option ONLY if you want basic calculations without authentication and do not need voice generation.

*   **Base URL**: `https://panchang.visionpair.cloud/api/panchanga`
*   **Authentication**: None
*   **Features**: Basic Panchanga data only (No Voice).

---

## Example: AI Agent Tool Definition

If you are using the **AI Agent** node, use **Option 1** for the best results.

**Tool Name**: `get_sankalpam_voice`
**Description**: `Generates audio and text for Hindu Sankalpam.`

**JSON Schema:**
```json
{
  "type": "object",
  "properties": {
    "latitude": { "type": "number" },
    "longitude": { "type": "number" },
    "timezone": { "type": "number" },
    "locationName": { "type": "string" },
    "year": { "type": "integer" },
    "month": { "type": "integer" },
    "day": { "type": "integer" }
  },
  "required": ["latitude", "longitude", "timezone"]
}
```

**Workflow Connection**:
*   Connect the tool to an **HTTP Request** node.
*   **URL**: `https://panchang-mcp.visionpair.cloud/api/voice`
*   **Header**: `X-API-Key: YOUR_SECRET_KEY`

# n8n Integration Guide

Since **n8n** is a workflow automation tool that excels at connecting to APIs, the best way to use your Panchangam service in n8n is to connect directly to your **REST API** (`panchang.visionpair.cloud`).

While the **MCP Server** (`panchang-mcp...`) is designed for AI clients like Claude Desktop or Cursor, **n8n** works best with the standard API endpoints.

## Option 1: Using with AI Agent (LangChain)

If you are building an AI Agent in n8n (using the **AI Agent** node), you should add a **Custom Tool**.

1.  Add a **Define Custom Tool** node (under LangChain > Tools).
2.  Connect it to your **AI Agent** node.
3.  Configure the tool as follows:

*   **Name**: `get_panchanga`
*   **Description**: `Retrieves accurate Hindu Panchangam details (Tithi, Nakshatra, Sankalpam) for a specific location and date.`
*   **Schema Type**: `JSON`

**JSON Schema:**
```json
{
  "type": "object",
  "properties": {
    "latitude": {
      "type": "number",
      "description": "Latitude of the location (e.g., 33.15)"
    },
    "longitude": {
      "type": "number",
      "description": "Longitude of the location (e.g., -96.82)"
    },
    "timezone": {
      "type": "number",
      "description": "Timezone offset from UTC (e.g., -6.0 for CST)"
    },
    "year": {
      "type": "integer",
      "description": "Year (optional, defaults to current)"
    },
    "month": {
      "type": "integer",
      "description": "Month (optional, defaults to current)"
    },
    "day": {
      "type": "integer",
      "description": "Day (optional, defaults to current)"
    },
    "locationName": {
      "type": "string",
      "description": "Name of the city/location"
    }
  },
  "required": ["latitude", "longitude", "timezone"]
}
```

4.  **Workflow Operation**:
    *   The tool will output the parameters.
    *   Connect the **Define Custom Tool** output to an **HTTP Request** node.
    *   **HTTP Request Node Config**:
        *   **Method**: `GET`
        *   **URL**: `https://panchang.visionpair.cloud/api/panchanga`
        *   **Authentication**: None (Public API)
        *   **Query Parameters**: Map the fields from the tool input (latitude, longitude, etc.).

## Option 2: Standard Workflow (HTTP Request)

If you just want to get data without an AI Agent:

1.  Add an **HTTP Request** node.
2.  **Method**: `GET`
3.  **URL**: `https://panchang.visionpair.cloud/api/panchanga`
4.  **Query Parameters**:
    *   `latitude`: `33.1507` (or value from previous node)
    *   `longitude`: `-96.8236`
    *   `timezone`: `-6.0`
    *   `locationName`: `Frisco`
5.  Execute the node to get the JSON response.

## Why not use the MCP Server URL?

The MCP Server (`panchang-mcp.visionpair.cloud`) uses the **SSE (Server-Sent Events)** protocol designed for desktop AI apps. n8n currently supports **REST APIs** natively. Since your project hosts both, using the REST API (`panchang.visionpair.cloud`) is faster, more reliable, and native to n8n.

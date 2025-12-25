# HTTP API Usage Guide

If you are unable to use the MCP integration in n8n, you can use the standard HTTP API endpoints provided by the Panchangam Service. These endpoints return the same high-precision data as the MCP tools.

## Base URL
The API is available at:
`https://panchang-mcp.visionpair.cloud`

## Authentication
You must provide your API Key in the request header or query parameter.

- **Header:** `X-API-Key: <YOUR_API_KEY>` (Recommended)
- **Query Param:** `?api_key=<YOUR_API_KEY>`

## Endpoints

### 1. Get Panchanga Data
Returns detailed Panchanga information (Tithi, Nakshatra, Sunrise, etc.).

- **Endpoint:** `GET /api/panchanga`
- **Parameters:**
  - `latitude` (float): Location latitude (e.g., 33.1507)
  - `longitude` (float): Location longitude (e.g., -96.8236)
  - `timezone` (float): Timezone offset (e.g., -6.0 for CST)
  - `date` (string, optional): Date in YYYY-MM-DD format (default: today)
  - `location_name` (string, optional): Name of the location

**Example Request (n8n HTTP Request Node):**
- **Method:** GET
- **URL:** `https://panchang-mcp.visionpair.cloud/api/panchanga`
- **Query Parameters:**
  - `latitude`: `33.1507`
  - `longitude`: `-96.8236`
  - `timezone`: `-6`
  - `date`: `2025-12-24`
- **Headers:**
  - `X-API-Key`: `pg_live_7K9vP2nRqW8vNzL4jYhF6tQsC3dGbU5nV1wX0aE8fT9iM7oA2kJ4pS6rH3uB`

### 2. Get Sankalpam Text
Returns the generated Sankalpam mantra text.

- **Endpoint:** `GET /api/sankalpam`
- **Parameters:** Same as above.

**Example Response:**
```json
{
  "sankalpam": "Śrī Śubha Viśvāvasu Nāma Samvatsare... Śukla Pakṣe Pañcamī..."
}
```

### 3. Get Sankalpam Audio
Returns the Sankalpam audio as a Base64 encoded string.

- **Endpoint:** `GET /api/voice`
- **Parameters:** Same as above.

**Example Response:**
```json
{
  "sankalpam_text": "...",
  "audio_base64": "SUQzBAAAAAAA..."
}
```

## Using in n8n
1. Add an **HTTP Request** node.
2. Set Method to **GET**.
3. Set URL to one of the endpoints above.
4. Add the **Query Parameters** for your location.
5. Under **Headers**, add `X-API-Key` with your key.
6. The output will contain the JSON data which you can map to other nodes.

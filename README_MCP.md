# Panchangam MCP Server

This project provides a **Model Context Protocol (MCP)** server for the Hindu Panchangam and Sankalpam generation service. It allows AI agents (like n8n, Claude Desktop, etc.) to access Panchanga data and generate Sankalpam audio.

## Features

- **Get Panchanga**: Retrieve detailed Hindu almanac data (Tithi, Nakshatra, Yoga, Karana, etc.).
- **High Precision**: Integrates `PyEphem` for astronomical accuracy (local sunrise, correct Tithi at sunrise), fixing common discrepancies in simplified models.
- **Get Sankalpam Text**: Generate the specific Sankalpam mantra for a location and date.
- **Get Sankalpam Audio**: Generate and retrieve a spoken audio file (MP3) of the Sankalpam using neural text-to-speech with correct Sanskrit pronunciation.
- **Secure Access**: API Key authentication.
- **Dockerized**: Easy deployment with Docker Compose.

## Prerequisites

- Docker and Docker Compose

## Quick Start

1.  **Clone the repository** (if not already done).
2.  **Run with Docker Compose**:

    ```bash
    docker-compose up --build -d
    ```

    This will start two services:
    - `panchanga-api`: The core .NET calculation engine (Port 8080).
    - `panchanga-mcp`: The Python MCP server (Port 8000).

## Configuration

You can configure the API Key by setting the `MCP_API_KEY` environment variable in `docker-compose.yml` or a `.env` file.

Default Key: `panchanga-secret-key`

## Connecting to Agents

### n8n (or generic MCP Client)

To connect this server to an MCP-compatible agent:

-   **Transport Type**: SSE (Server-Sent Events)
-   **Server URL**: `http://<your-vps-ip>:8000/sse`
-   **Authentication**: Custom Header
    -   **Header Name**: `X-API-Key`
    -   **Value**: `panchanga-secret-key` (or your configured key)

### Tools Available

1.  `get_panchanga_data(latitude, longitude, timezone, ...)`
2.  `get_sankalpam_text(latitude, longitude, timezone, ...)`
3.  `get_sankalpam_audio(latitude, longitude, timezone, ...)`
    -   Returns: JSON containing `audio_base64` string of the MP3 file.

## Security Note

When hosting on a VPS, ensure that:
1.  You change the default `MCP_API_KEY` to a strong secret.
2.  You expose only the necessary ports. The MCP server is on port 8000.
3.  If connecting over the public internet, consider setting up a reverse proxy (Nginx/Caddy) with HTTPS (SSL/TLS) in front of the container, as SSE over plain HTTP can be insecure.

## Local Development (Python)

To run the MCP server locally without Docker:

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the .NET API separately (or point to a deployed instance via `PANCHANGAM_API_URL`).
3.  Run the server:
    ```bash
    python mcp_server.py
    ```

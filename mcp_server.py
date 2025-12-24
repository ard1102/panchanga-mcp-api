import os
import uvicorn
import base64
import uuid
from fastapi import FastAPI, Request, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
from panchanga_tool import get_panchanga, get_sankalpam, get_sankalpam_voice

# Configuration
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("MCP_API_KEY", "panchanga-secret-key")

# Initialize FastMCP
# We set host="0.0.0.0" to ensure it binds/allows all interfaces, though we mount it manually.
# This helps prevent "Invalid Host header" (421) errors if FastMCP sets up TrustedHostMiddleware.
mcp = FastMCP("Panchangam Service", host="0.0.0.0")

# -----------------------------------------------------------------------------
# Tool Definitions
# -----------------------------------------------------------------------------

@mcp.tool()
def get_panchanga_data(latitude: float, longitude: float, timezone: float, year: int = None, month: int = None, day: int = None, location_name: str = "Unknown"):
    """
    Get the Hindu Panchanga details for a specific location and date.
    Returns Tithi, Nakshatra, Yoga, Karana, Vara, Sunrise, Sunset, etc.
    """
    return get_panchanga(latitude, longitude, timezone, year, month, day, location_name)

@mcp.tool()
def get_sankalpam_text(latitude: float, longitude: float, timezone: float, year: int = None, month: int = None, day: int = None, location_name: str = "Unknown"):
    """
    Get the Sankalpam mantra text for a specific location and date.
    Includes Samvatsara, Ayana, Ritu, Masa, Paksha, Tithi, Vara, Nakshatra.
    """
    return get_sankalpam(latitude, longitude, timezone, year, month, day, location_name)

@mcp.tool()
def get_sankalpam_audio(latitude: float, longitude: float, timezone: float, year: int = None, month: int = None, day: int = None, location_name: str = "Unknown"):
    """
    Get the Sankalpam audio as a base64 encoded MP3 string.
    Returns JSON with 'sankalpam_text', 'sankalpam_devanagari', and 'audio_base64'.
    """
    # Generate audio
    # The tool now generates a unique filename based on location and time.
    # It also handles cleanup of old files automatically.
    
    result = get_sankalpam_voice(latitude, longitude, timezone, year, month, day, location_name)
    
    if "error" in result:
        return result
        
    audio_path = result.get("audio_file")
    if audio_path and os.path.exists(audio_path):
        try:
            with open(audio_path, "rb") as audio_file:
                encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
                
            result["audio_base64"] = encoded_string
            # Cleanup
            # os.remove(audio_path) 
        except Exception as e:
            return {"error": f"Failed to encode audio: {str(e)}"}
            
    return result

# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------

class APIKeyMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        path = request.url.path
        
        # Allow health checks or open endpoints
        if path in ["/health", "/docs", "/openapi.json"]:
             await self.app(scope, receive, send)
             return
             
        # 1. Check Header
        api_key = request.headers.get(API_KEY_NAME)
        if not api_key:
            api_key = request.headers.get("MCP_API_KEY") # Fallback for user convenience
        
        # 2. Check Query Parameter (if header is missing)
        if not api_key:
            api_key = request.query_params.get("api_key")

        if not api_key or api_key != API_KEY:
             print(f"AUTH FAILED: Path={path}, Received={api_key}")
             response = JSONResponse(status_code=403, content={"detail": "Invalid or missing API Key"})
             await response(scope, receive, send)
             return
             
        await self.app(scope, receive, send)

# -----------------------------------------------------------------------------
# Server Application Expose
# -----------------------------------------------------------------------------

# Create a secure wrapper application
secure_app = FastAPI()
secure_app.add_middleware(APIKeyMiddleware)

@secure_app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    print(f"CRITICAL ERROR in {request.url.path}: {exc}")
    print(error_detail)
    return JSONResponse(status_code=500, content={"detail": str(exc), "trace": error_detail})

@secure_app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "panchanga-mcp"}

# -----------------------------------------------------------------------------
# REST Endpoints for n8n / External Apps
# -----------------------------------------------------------------------------

@secure_app.get("/api/panchanga")
async def rest_get_panchanga(
    latitude: float, 
    longitude: float, 
    timezone: float, 
    year: int = None, 
    month: int = None, 
    day: int = None, 
    location_name: str = "Unknown"
):
    """REST endpoint to get Panchanga data (High Precision)"""
    return get_panchanga(latitude, longitude, timezone, year, month, day, location_name)

@secure_app.get("/api/sankalpam")
async def rest_get_sankalpam(
    latitude: float, 
    longitude: float, 
    timezone: float, 
    year: int = None, 
    month: int = None, 
    day: int = None, 
    location_name: str = "Unknown"
):
    """REST endpoint to get Sankalpam text"""
    return get_sankalpam(latitude, longitude, timezone, year, month, day, location_name)

@secure_app.get("/api/voice")
async def rest_get_voice(
    latitude: float, 
    longitude: float, 
    timezone: float, 
    year: int = None, 
    month: int = None, 
    day: int = None, 
    location_name: str = "Unknown"
):
    """REST endpoint to get Sankalpam Audio (Base64)"""
    result = get_sankalpam_voice(latitude, longitude, timezone, year, month, day, location_name)
    
    # Handle error or file reading logic (duplicated from tool for safety)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
        
    audio_path = result.get("audio_file")
    if audio_path and os.path.exists(audio_path):
        try:
            with open(audio_path, "rb") as audio_file:
                encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            result["audio_base64"] = encoded_string
            # Optional: Cleanup is handled in get_sankalpam_voice mostly, but we can do it here too if needed
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to encode audio: {str(e)}"})
            
    return result

# Mount the MCP server
# FastMCP instances are ASGI applications
secure_app.mount("/", mcp.sse_app())

if __name__ == "__main__":
    print(f"Starting MCP Server on port 8000...")
    print(f"API Key required: {API_KEY_NAME}: {API_KEY}")
    uvicorn.run(secure_app, host="0.0.0.0", port=8000)

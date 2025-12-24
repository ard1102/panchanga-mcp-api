import httpx
import asyncio
import os

URL = "http://localhost:9000/sse"
API_KEY = os.getenv("MCP_API_KEY", "panchanga-secret-key")

async def test_connection():
    print(f"Testing local connection to {URL}")
    headers = {"X-API-Key": API_KEY}
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            async with client.stream("GET", URL, headers=headers) as response:
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    print("Success! Connection established.")
                    # Optionally read a bit of the stream
                    async for chunk in response.aiter_lines():
                        print(f"Received chunk: {chunk}")
                        break # Just one chunk is enough to prove it works
                else:
                    print(f"Failed with status: {response.status_code}")
                    print(await response.aread())
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())

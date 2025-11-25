import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Configuration
MEMORY_SERVICE_URL = os.getenv("MEMORY_SERVICE_URL", "http://memory-service.railway.internal:8000")
VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://voice-service.railway.internal:8000")
SCHEDULER_SERVICE_URL = os.getenv("SCHEDULER_SERVICE_URL", "http://scheduler-service.railway.internal:8000")
INTEGRATION_HUB_URL = os.getenv("INTEGRATION_HUB_URL", "http://integration-hub.railway.internal:8000")

@app.get("/")
async def root():
    return {"message": "Atlas API Gateway"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

async def proxy_request(url: str, method: str, payload: dict = None):
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, timeout=30.0)
            elif method == "POST":
                response = await client.post(url, json=payload, timeout=30.0)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"An error occurred while requesting {exc.request.url!r}.")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")

@app.post("/chat")
async def chat_proxy(request: Request):
    payload = await request.json()
    return await proxy_request(f"{MEMORY_SERVICE_URL}/chat", "POST", payload)

# Add other proxies as needed

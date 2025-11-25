from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Integration Hub"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

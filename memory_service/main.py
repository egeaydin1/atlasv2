import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import openai
from anthropic import Anthropic
from qdrant_client import QdrantClient
from qdrant_client.http import models

import qdrant_client as qc
print(f"Qdrant Client Version: {qc.__version__}")

app = FastAPI()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

# Initialize Clients
openai.api_key = OPENAI_API_KEY
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL)

COLLECTION_NAME = "memories"

# Ensure Qdrant Collection Exists
try:
    qdrant_client.get_collection(COLLECTION_NAME)
except Exception:
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
    )

class ChatRequest(BaseModel):
    user_id: str
    text: str

class ChatResponse(BaseModel):
    response: str

def get_embedding(text: str) -> List[float]:
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search_context(query_vector: List[float], limit: int = 5) -> str:
    # Use search method explicitly
    hits = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )
    return "\n".join([hit.payload["text"] for hit in hits if hit.payload])

def save_memory(text: str, vector: List[float]):
    import uuid
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": text}
            )
        ]
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 1. Generate Embedding
        query_vector = get_embedding(request.text)

        # 2. Search Context (RAG)
        context = search_context(query_vector)

        # 3. Construct Prompt
        system_prompt = f"""You are Atlas, a proactive AI assistant.
        Use the following context from previous conversations to answer the user's request.
        
        Context:
        {context}
        """

        # 4. Call Claude 3.5 Sonnet
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": request.text}
            ]
        )
        response_text = message.content[0].text

        # 5. Save Interaction to Memory (User Query + AI Response)
        # We save them separately or together. For simplicity, saving user query now.
        # Ideally, we should save both.
        import uuid
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=query_vector,
                    payload={"text": f"User: {request.text}\nAtlas: {response_text}"}
                )
            ]
        )

        return ChatResponse(response=response_text)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI(title="Finance Assistant Orchestrator")

# Configuration
AGENT_URLS = {
    "api": os.getenv("API_AGENT_URL", "http://localhost:8001"),
    "scraping": os.getenv("SCRAPING_AGENT_URL", "http://localhost:8002"),
    "retriever": os.getenv("RETRIEVER_AGENT_URL", "http://localhost:8003"),
    "analysis": os.getenv("ANALYSIS_AGENT_URL", "http://localhost:8004"),
    "language": os.getenv("LANGUAGE_AGENT_URL", "http://localhost:8005"),
    "voice": os.getenv("VOICE_AGENT_URL", "http://localhost:8006"),
}

class ChatRequest(BaseModel):
    message: str
    use_voice: bool = False

class MarketOverview(BaseModel):
    summary: str
    metrics: Dict[str, Any]
    timestamp: datetime

@app.get("/")
async def root():
    return {"status": "healthy", "service": "orchestrator"}

@app.get("/market/overview")
async def get_market_overview():
    try:
        async with httpx.AsyncClient() as client:
            # Get market data from API agent
            api_response = await client.get(f"{AGENT_URLS['api']}/market-data")
            market_data = api_response.json()

            # Get analysis from analysis agent
            analysis_response = await client.post(
                f"{AGENT_URLS['analysis']}/analyze",
                json=market_data
            )
            analysis = analysis_response.json()

            # Get news from scraping agent
            news_response = await client.get(f"{AGENT_URLS['scraping']}/news")
            news = news_response.json()

            # Combine all data
            overview = {
                "summary": analysis["summary"],
                "metrics": market_data["metrics"],
                "news": news[:5],
                "timestamp": datetime.now().isoformat()
            }

            return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def process_chat(request: ChatRequest):
    try:
        async with httpx.AsyncClient() as client:
            # If voice input, process through voice agent first
            if request.use_voice:
                voice_response = await client.post(
                    f"{AGENT_URLS['voice']}/process",
                    json={"audio": request.message}
                )
                text_input = voice_response.json()["text"]
            else:
                text_input = request.message

            # Get relevant context from retriever agent
            context_response = await client.post(
                f"{AGENT_URLS['retriever']}/search",
                json={"query": text_input}
            )
            context = context_response.json()

            # Get market data if needed
            market_response = await client.get(f"{AGENT_URLS['api']}/market-data")
            market_data = market_response.json()

            # Generate response using language agent
            response = await client.post(
                f"{AGENT_URLS['language']}/generate",
                json={
                    "query": text_input,
                    "context": context,
                    "market_data": market_data
                }
            )

            # If voice output is requested, convert to speech
            if request.use_voice:
                voice_output = await client.post(
                    f"{AGENT_URLS['voice']}/synthesize",
                    json={"text": response.json()["response"]}
                )
                return {
                    "response": response.json()["response"],
                    "audio": voice_output.json()["audio"]
                }

            return {"response": response.json()["response"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news")
async def get_news():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENT_URLS['scraping']}/news")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
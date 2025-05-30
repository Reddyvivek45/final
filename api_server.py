from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import List, Dict, Any
from datetime import datetime

# Import utility modules
from utils.language_agent import generate_with_groq, construct_prompt, format_market_data
from utils.retriever_agent import search_documents, SearchResults

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI Models
class ChatRequest(BaseModel):
    query: str
    market_data: Dict[str, Any] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    sources: List[str]

# FastAPI Routes
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Search for relevant documents
        search_results = search_documents(request.query)
        
        # Construct context from search results
        context = " ".join([result.text for result in search_results.results]) if search_results.results else ""
        
        # Format market data
        market_summary = format_market_data(request.market_data)
        
        # Construct prompt
        prompt = construct_prompt(request.query, context, market_summary)
        
        # Generate response
        response = await generate_with_groq(prompt)
        
        # Calculate confidence
        confidence = 0.8 if search_results.results else 0.5
        
        # Get sources
        sources = [result.metadata.get("source", "Unknown") for result in search_results.results]
        
        return ChatResponse(
            response=response,
            confidence=confidence,
            sources=sources
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-overview")
async def market_overview():
    try:
        # Return dummy market data
        market_data = {
            "stocks": [
                {"symbol": "AAPL", "price": 150.0, "change": 2.5},
                {"symbol": "GOOGL", "price": 2800.0, "change": 1.8},
                {"symbol": "MSFT", "price": 300.0, "change": 3.2}
            ],
            "metrics": {
                "total_value": 5000,
                "avg_change": 2.5,
                "total_volume": 1000000
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return market_data
    except Exception as e:
        logger.error(f"Error in market overview endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
from fastapi import FastAPI, HTTPException, Body
from datetime import datetime
from utils.api_agent import fetch_market_data
from utils.analysis_agent import (
    calculate_volatility,
    calculate_beta,
    generate_insights,
    determine_risk_level,
    determine_sentiment
)
from utils.language_agent import (
    format_market_data,
    construct_prompt,
    generate_with_groq,
    calculate_confidence
)
from utils.retriever_agent import search_documents
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

# Initialize FastAPI app
app = FastAPI(
    title="Finance Assistant API",
    description="API for market analysis and insights",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for favicon
from fastapi.staticfiles import StaticFiles
import os
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Root endpoint
@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Finance Assistant API is running",
        "endpoints": {
            "market_overview": "/market/overview",
            "chat": "/chat",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Market overview endpoint
@app.get("/market/overview")
async def get_market_overview():
    try:
        # Fetch market data for some default symbols
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN"]
        market_data = await fetch_market_data(symbols)
        
        # Ensure we have valid data
        if not market_data or not market_data.get("stocks"):
            return {
                "status": "success",
                "data": {
                    "market_data": {
                        "stocks": [],
                        "metrics": {
                            "total_value": 0,
                            "avg_change": 0,
                            "total_volume": 0
                        }
                    },
                    "analysis": {
                        "volatility": 0,
                        "beta": 0,
                        "insights": ["No market data available"],
                        "risk_level": "Unknown",
                        "sentiment": "Neutral"
                    }
                }
            }
        
        # Calculate analysis metrics with error handling
        try:
            volatility = calculate_volatility(market_data["stocks"])
            beta = calculate_beta(market_data["stocks"])
        except (ValueError, ZeroDivisionError):
            volatility = 0
            beta = 0
        
        # Generate insights
        weighted_change = market_data["metrics"].get("avg_change", 0)
        insights = generate_insights(market_data["stocks"], weighted_change, volatility)
        
        # Determine risk and sentiment
        risk_level = determine_risk_level(volatility, beta)
        sentiment = determine_sentiment(weighted_change, volatility)
        
        return {
            "status": "success",
            "data": {
                "market_data": market_data,
                "analysis": {
                    "volatility": float(volatility),  # Convert numpy float to Python float
                    "beta": float(beta),  # Convert numpy float to Python float
                    "insights": insights,
                    "risk_level": risk_level,
                    "sentiment": sentiment
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat request model
class ChatRequest(BaseModel):
    query: str

# Chat endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Get market data
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN"]
        market_data = await fetch_market_data(symbols)
        
        # Search for relevant documents
        search_results = search_documents(request.query)
        context = "\n".join([r["text"] for r in search_results.results]) if search_results.results else ""
        
        # Format market data
        market_summary = format_market_data(market_data)
        
        # Construct prompt
        prompt = construct_prompt(
            query=request.query,
            context=context,
            market_summary=market_summary
        )
        
        # Generate response
        response = await generate_with_groq(prompt)
        
        # Calculate confidence
        confidence = calculate_confidence(response, search_results.results)
        
        return {
            "status": "success",
            "data": {
                "response": response,
                "confidence": confidence,
                "sources": [r["metadata"] for r in search_results.results] if search_results.results else []
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
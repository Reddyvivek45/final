from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import requests
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketData(BaseModel):
    metrics: Dict[str, Any]
    stocks: Dict[str, Any]
    timestamp: str

async def fetch_market_data(symbols: list) -> Dict[str, Any]:
    """Fetch market data from Alpha Vantage API"""
    try:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY not found in environment variables")

        data = {"metrics": {}, "stocks": {}, "timestamp": datetime.now().isoformat()}
        
        for symbol in symbols:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            quote = response.json().get("Global Quote", {})
            if quote:
                data["stocks"][symbol] = {
                    "price": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": float(quote.get("10. change percent", "0").replace("%", "")),
                    "volume": int(quote.get("06. volume", 0))
                }
        
        # Calculate portfolio metrics
        if data["stocks"]:
            data["metrics"] = {
                "total_value": sum(stock["price"] for stock in data["stocks"].values()),
                "avg_change": sum(stock["change_percent"] for stock in data["stocks"].values()) / len(data["stocks"]),
                "total_volume": sum(stock["volume"] for stock in data["stocks"].values())
            }
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
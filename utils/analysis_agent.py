from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from sklearn.preprocessing import MinMaxScaler
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketData(BaseModel):
    metrics: Dict[str, Any]
    stocks: Dict[str, Any]
    timestamp: str

class AnalysisResult(BaseModel):
    summary: str
    metrics: Dict[str, Any]
    insights: List[str]
    risk_level: str
    sentiment: str

def calculate_volatility(stocks_data: Dict[str, Any]) -> float:
    """Calculate portfolio volatility"""
    try:
        changes = [stock["change"] for stock in stocks_data.values()]
        return np.std(changes)
    except Exception as e:
        logger.warning(f"Error calculating volatility: {str(e)}")
        return 0.0

def calculate_beta(stocks_data: Dict[str, Any]) -> float:
    """Calculate portfolio beta"""
    try:
        # Simplified beta calculation
        market_changes = [stock["change"] for stock in stocks_data.values()]
        return np.mean(market_changes)
    except Exception as e:
        logger.warning(f"Error calculating beta: {str(e)}")
        return 1.0

def generate_insights(
    stocks_data: Dict[str, Any],
    weighted_change: float,
    volatility: float
) -> List[str]:
    """Generate market insights"""
    insights = []        # Calculate portfolio metrics

    
    return insights

def determine_risk_level(volatility: float, beta: float) -> str:
    """Determine portfolio risk level"""
    if volatility > 3 and beta > 1.5:
        return "High"
    elif volatility > 2 or beta > 1.2:
        return "Moderate"
    else:
        return "Low"

def determine_sentiment(weighted_change: float, volatility: float) -> str:
    """Determine market sentiment"""
    if weighted_change > 2 and volatility < 2:
        return "Bullish"
    elif weighted_change < -2 and volatility > 2:
        return "Bearish"
    elif volatility > 2:
        return "Cautious"
    else:
        return "Neutral"
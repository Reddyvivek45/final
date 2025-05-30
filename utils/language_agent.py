from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from groq import Groq
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Fallback responses for when API is unavailable
FALLBACK_RESPONSES = [
    "I apologize, but I'm currently unable to access my full capabilities. Please try again later or rephrase your question.",
    "I'm experiencing some technical difficulties. Could you please try again in a few moments?",
    "I'm temporarily limited in my ability to process your request. Please try again later.",
    "I'm unable to provide a detailed response at the moment. Please try again in a few minutes."
]

class GenerationRequest(BaseModel):
    query: str
    context: List[Dict[str, Any]]
    market_data: Dict[str, Any]

class GenerationResponse(BaseModel):
    response: str
    confidence: float
    sources: List[str]

def format_market_data(market_data: Dict[str, Any]) -> str:
    """Format market data into a readable string"""
    try:
        stocks = market_data.get("stocks", [])
        metrics = market_data.get("metrics", {})
        
        summary = "Market Overview:\n"
        
        # Add stock information
        if stocks:
            summary += "\nStock Performance:\n"
            for stock in stocks:
                summary += f"- {stock['symbol']}: ${stock['price']:.2f} ({stock['change']:+.2f}%)\n"
        
        # Add market metrics
        if metrics:
            summary += f"\nMarket Metrics:\n"
            summary += f"- Total Value: ${metrics.get('total_value', 0):,.2f}B\n"
            summary += f"- Average Change: {metrics.get('avg_change', 0):+.2f}%\n"
            summary += f"- Total Volume: {metrics.get('total_volume', 0):,}\n"
        
        return summary
    except Exception as e:
        logger.error(f"Error formatting market data: {str(e)}")
        return "Error formatting market data"

def construct_prompt(query: str, context: str = "", market_summary: str = "") -> str:
    """Construct a prompt for the language model"""
    prompt = f"""You are a financial analysis assistant. Use the following information to answer the user's question:

Market Summary:
{market_summary}

Relevant Context:
{context}

User Question: {query}

Please provide a clear and concise response based on the available information. If you're not sure about something, say so.
"""
    return prompt

async def generate_with_groq(prompt: str, max_retries: int = 3) -> str:
    """Generate a response using Groq's API with retry logic"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="qwen-qwq-32b",
                messages=[
                    {"role": "system", "content": "You are a helpful financial analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error calling Groq API (attempt {attempt + 1}/{max_retries}): {error_msg}")
            
            # Check for quota exceeded error
            if "insufficient_quota" in error_msg or "429" in error_msg:
                if attempt == max_retries - 1:  # Last attempt
                    return FALLBACK_RESPONSES[attempt % len(FALLBACK_RESPONSES)]
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return "I apologize, but I encountered an error while processing your request. Please try again later."
    
    return FALLBACK_RESPONSES[-1]

def calculate_confidence(response: str, search_results: List[Dict[str, Any]]) -> float:
    """Calculate confidence score for the response"""
    try:
        # Simple confidence calculation based on response length and search results
        base_confidence = 0.5
        
        # Adjust based on response length
        if len(response) > 100:
            base_confidence += 0.2
        
        # Adjust based on search results
        if search_results:
            base_confidence += 0.3
        
        return min(base_confidence, 1.0)
    except Exception as e:
        logger.error(f"Error calculating confidence: {str(e)}")
        return 0.5 
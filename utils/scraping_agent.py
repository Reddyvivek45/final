from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import asyncio
import aiohttp
from newspaper import Article
import logging
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsItem(BaseModel):
    title: str
    url: str
    source: str
    summary: str
    published_at: datetime
    sentiment: float = 0.0

async def fetch_news(symbols: List[str], days: int = 7) -> List[NewsItem]:
    """Fetch news articles for given symbols"""
    try:
        news_items = []
        async with aiohttp.ClientSession() as session:
            for symbol in symbols:
                # Fetch news from Yahoo Finance
                url = f"https://finance.yahoo.com/quote/{symbol}/news"
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract news articles
                        articles = soup.find_all('div', {'class': 'js-content-viewer'})
                        for article in articles[:5]:  # Limit to 5 articles per symbol
                            try:
                                link = article.find('a')['href']
                                if not link.startswith('http'):
                                    link = f"https://finance.yahoo.com{link}"
                                
                                # Get article details
                                article_obj = Article(link)
                                article_obj.download()
                                article_obj.parse()
                                
                                news_items.append(NewsItem(
                                    title=article_obj.title,
                                    url=link,
                                    source="Yahoo Finance",
                                    summary=article_obj.summary,
                                    published_at=article_obj.publish_date or datetime.now(),
                                    sentiment=0.0  # Sentiment analysis can be added here
                                ))
                            except Exception as e:
                                logger.warning(f"Error processing article: {str(e)}")
                                continue
                    
        return news_items
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_stock_data(symbol: str) -> Dict[str, Any]:
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        return {
            "symbol": symbol,
            "price": info.get("regularMarketPrice", 0),
            "change": info.get("regularMarketChangePercent", 0),
            "volume": info.get("regularMarketVolume", 0),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "dividend_yield": info.get("dividendYield", 0)
        }
        
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def fetch_news_articles(query: str = "", max_articles: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch financial news articles from various sources.
    Currently returns dummy data as a placeholder.
    """
    try:
        # TODO: Implement actual news scraping
        # For now, return dummy data
        dummy_articles = [
            {
                "title": "Tech Stocks Show Strong Growth",
                "source": "Financial Times",
                "url": "https://example.com/article1",
                "summary": "Technology stocks continue to show strong performance in the market.",
                "date": "2024-03-15"
            },
            {
                "title": "Federal Reserve Maintains Interest Rates",
                "source": "Wall Street Journal",
                "url": "https://example.com/article2",
                "summary": "The Federal Reserve has decided to keep interest rates unchanged.",
                "date": "2024-03-14"
            },
            {
                "title": "Global Markets Face Volatility",
                "source": "Bloomberg",
                "url": "https://example.com/article3",
                "summary": "Global markets are experiencing increased volatility due to geopolitical tensions.",
                "date": "2024-03-13"
            }
        ]
        
        return dummy_articles[:max_articles]
    except Exception as e:
        logger.error(f"Error fetching news articles: {str(e)}")
        return []
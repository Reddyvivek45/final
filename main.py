import streamlit as st
import requests
import json
import os
import logging
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import speech_recognition as sr
from gtts import gTTS
import io
import base64
import time

# Import utility modules
from utils.language_agent import generate_with_groq, construct_prompt, format_market_data
from utils.retriever_agent import search_documents, SearchResults
from utils.scraping_agent import fetch_news_articles
from utils.voice_agent import text_to_speech, speech_to_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'market_data' not in st.session_state:
    st.session_state.market_data = {
        "stocks": [
            {"symbol": "AAPL", "price": 150.0, "change": 2.5},
            {"symbol": "GOOGL", "price": 2800.0, "change": 1.8},
            {"symbol": "MSFT", "price": 300.0, "change": 3.2}
        ],
        "metrics": {
            "total_value": 5000,
            "avg_change": 2.5,
            "total_volume": 1000000
        }
    }

# Streamlit UI
def main():
    # Set page config
    st.set_page_config(
        page_title="Financial Analysis Assistant",
        page_icon="📈",
        layout="wide"
    )
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .chat-message.user {
            background-color: #2b313e;
        }
        .chat-message.assistant {
            background-color: #1e1e1e;
        }
        .chat-message .content {
            display: flex;
            margin-top: 0.5rem;
        }
        .stButton button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📈 Financial Analysis Assistant")
    
    # Sidebar
    with st.sidebar:
        st.title("Market Overview")
        
        # Fetch market data with retry
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get("http://localhost:8000/api/market-overview")
                if response.status_code == 200:
                    market_data = response.json()
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    st.error("Failed to fetch market data. Using cached data.")
                    market_data = st.session_state.market_data
                else:
                    time.sleep(retry_delay)
        
        # Display market metrics
        metrics = market_data["metrics"]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Value", f"${metrics['total_value']:,.2f}B")
        with col2:
            st.metric("Avg Change", f"{metrics['avg_change']:+.2f}%")
        with col3:
            st.metric("Volume", f"{metrics['total_volume']:,}")
        
        # Display stock performance
        st.subheader("Stock Performance")
        stocks_df = pd.DataFrame(market_data["stocks"])
        st.dataframe(stocks_df)
        
        # Display recent news
        st.subheader("Recent News")
        news_articles = fetch_news_articles()
        for article in news_articles:
            with st.expander(article["title"]):
                st.write(f"Source: {article['source']}")
                st.write(f"Date: {article['date']}")
                st.write(article["summary"])
    
    # Main chat interface
    st.subheader("Chat with the Assistant")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message.get("audio"):
                st.audio(message["audio"], format="audio/mp3")
    
    # Chat input with voice
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.chat_input("Ask a question about the market...")
    with col2:
        if st.button("🎤", help="Click to use voice input"):
            try:
                query = speech_to_text()
                if query:
                    st.session_state.last_query = query
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Error with voice input: {str(e)}")
    
    if query:
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        # Get response from API
        try:
            response = requests.post(
                "http://localhost:8000/api/chat",
                json={"query": query, "market_data": market_data}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Generate audio for response
                try:
                    audio = text_to_speech(result["response"])
                    audio_b64 = base64.b64encode(audio.getvalue()).decode()
                except Exception as e:
                    logger.error(f"Error generating audio: {str(e)}")
                    audio_b64 = None
                
                # Add assistant message to chat
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result["response"],
                    "audio": audio_b64
                })
                
                # Display confidence and sources
                st.info(f"Confidence: {result['confidence']:.2%}")
                if result["sources"]:
                    st.info(f"Sources: {', '.join(result['sources'])}")
                
                st.experimental_rerun()
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
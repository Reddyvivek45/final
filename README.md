# Finance Assistant

A comprehensive financial analysis and market insights platform powered by Groq's Qwen model.

## Features

- Real-time market data processing
- Voice-based interaction
- RAG-powered market insights
- Multi-agent orchestration
- Quantitative analysis
- Interactive Streamlit interface

## Prerequisites

1. **System Requirements**
   - Python 3.9+
   - Docker and Docker Compose
   - Git

2. **API Keys**
   - Groq API Key (for Qwen model)
   - Alpha Vantage API Key (for market data)

## Installation

```bash
# Clone the repository
git clone [repository-url]
cd finance-assistant

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Setup

1. Copy `.env.example` to `.env`
2. Add your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
   ```

## Running the Application

```bash
# Start the services
docker-compose up -d

# Run the Streamlit app
streamlit run streamlit_app/main.py
```

## Project Structure

```
finance-assistant/
├── agents/              # Agent implementations
├── data_ingestion/      # Data pipeline components
├── orchestrator/        # FastAPI orchestration service
├── streamlit_app/       # Frontend application
├── docs/               # Documentation
├── tests/              # Test suite
└── docker/             # Docker configuration
```

## Technologies Used

- **Frameworks**: FastAPI, Streamlit, LangChain
- **Vector Store**: FAISS
- **Voice Processing**: Whisper
- **LLM Integration**: Groq (Qwen-32B)
- **Data Processing**: Pandas, NumPy
- **Containerization**: Docker

## Features in Detail

### Market Analysis
- Real-time stock data processing
- Technical indicators calculation
- Market sentiment analysis
- Risk assessment

### Voice Interaction
- Speech-to-text conversion
- Text-to-speech synthesis
- Natural language understanding

### Data Processing
- Market data aggregation
- News article processing
- Document retrieval and analysis

### User Interface
- Interactive Streamlit dashboard
- Real-time market updates
- Chat interface with voice support
- Market metrics visualization

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Groq for the Qwen model
- Streamlit for the frontend framework
- FastAPI for the backend services
- Alpha Vantage for market data

# Multi-Agent Finance Assistant

A sophisticated multi-source, multi-agent finance assistant that delivers spoken market briefs via a Streamlit app. The system leverages advanced data ingestion pipelines, vector stores for RAG, and specialized agents orchestrated through FastAPI microservices.

## Architecture

### Agent Components

1. **API Agent**
   - Real-time & historical market data via AlphaVantage/Yahoo Finance
   - Handles market data retrieval and processing

2. **Scraping Agent**
   - Crawls financial filings and news
   - Implements efficient document loading and processing

3. **Retriever Agent**
   - Manages vector embeddings in FAISS
   - Handles semantic search and retrieval

4. **Analysis Agent**
   - Processes market data and generates insights
   - Performs quantitative analysis

5. **Language Agent**
   - Synthesizes narratives using LLM
   - Implements RAG for context-aware responses

6. **Voice Agent**
   - Handles Speech-to-Text (Whisper)
   - Manages Text-to-Speech conversion
   - Processes voice input/output pipelines

### System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Streamlit  │────▶│ FastAPI     │────▶│   Agents    │
│    Frontend │     │ Orchestrator│     │  (Micro-    │
└─────────────┘     └─────────────┘     │  services)  │
                                         └─────────────┘
                                               │
                                         ┌─────┴─────┐
                                         │  Vector   │
                                         │  Store    │
                                         └───────────┘
```

## Setup Instructions

1. **Prerequisites**
   - Python 3.9+
   - Docker and Docker Compose
   - Git

2. **Installation**
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

3. **Environment Setup**
   - Copy `.env.example` to `.env`
   - Fill in required API keys and configuration

4. **Running the Application**
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

## Features

- Real-time market data processing
- Voice-based interaction
- RAG-powered market insights
- Multi-agent orchestration
- Quantitative analysis
- Interactive Streamlit interface

## Technologies Used

- **Frameworks**: FastAPI, Streamlit, LangChain
- **Vector Store**: FAISS
- **Voice Processing**: Whisper
- **LLM Integration**: OpenAI GPT
- **Data Processing**: Pandas, NumPy
- **Containerization**: Docker

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT and Whisper models
- Streamlit for the frontend framework
- FastAPI for the backend services 

OPENAI_API_KEY="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"
ALPHA_VANTAGE_API_KEY="AGSGCFXHD45CGYFX"
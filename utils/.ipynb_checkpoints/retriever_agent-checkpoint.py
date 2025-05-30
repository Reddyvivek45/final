from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import faiss
import numpy as np
import json
import os
import logging
from datetime import datetime
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Force CPU usage
os.environ["CUDA_VISIBLE_DEVICES"] = ""
torch.set_num_threads(4)  # Limit CPU threads

# Initialize global variables
index = None
documents = []
model = None

@dataclass
class SearchResult:
    text: str
    metadata: Dict[str, Any]

@dataclass
class SearchResults:
    results: List[SearchResult]

class RetrieverAgent:
    def __init__(self):
        self.model = None
        self.index = None
        self.documents = []
        self.initialize()

    def initialize(self):
        """Initialize the retriever with fallback options"""
        try:
            # Try to load the model with CPU explicitly
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            logger.info("Successfully loaded SentenceTransformer model on CPU")
        except Exception as e:
            logger.warning(f"Failed to load SentenceTransformer model: {str(e)}")
            logger.info("Using fallback document search functionality")
            self.model = None

        # Load fallback documents
        try:
            with open('data/fallback_docs.json', 'r') as f:
                self.documents = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load fallback documents: {str(e)}")
            self.documents = []

    def search_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search documents with fallback to keyword matching"""
        if not self.model:
            # Fallback to simple keyword matching
            return self._keyword_search(query, top_k)

        try:
            # Encode query
            query_vector = self.model.encode([query])[0]
            
            # Create FAISS index if not exists
            if self.index is None:
                dimension = query_vector.shape[0]
                self.index = faiss.IndexFlatL2(dimension)
                if self.documents:
                    doc_vectors = self.model.encode([doc['text'] for doc in self.documents])
                    self.index.add(np.array(doc_vectors).astype('float32'))

            # Search
            distances, indices = self.index.search(
                np.array([query_vector]).astype('float32'), 
                min(top_k, len(self.documents))
            )

            # Return results
            return [self.documents[i] for i in indices[0]]
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Simple keyword-based search as fallback"""
        query_words = set(query.lower().split())
        results = []
        
        for doc in self.documents:
            doc_words = set(doc['text'].lower().split())
            score = len(query_words.intersection(doc_words))
            if score > 0:
                results.append((score, doc))
        
        # Sort by score and return top_k results
        results.sort(reverse=True)
        return [doc for _, doc in results[:top_k]]

    def add_document(self, text: str, metadata: Dict[str, Any] = None):
        """Add a new document to the index"""
        if metadata is None:
            metadata = {}
        
        doc = {
            'text': text,
            'metadata': metadata
        }
        
        self.documents.append(doc)
        
        # Update FAISS index if model is available
        if self.model and self.index is not None:
            try:
                doc_vector = self.model.encode([text])[0]
                self.index.add(np.array([doc_vector]).astype('float32'))
            except Exception as e:
                logger.error(f"Error adding document to index: {str(e)}")

# Initialize global retriever instance
retriever = RetrieverAgent()

def search_documents(query: str, top_k: int = 3) -> SearchResults:
    """
    Global function to search documents using the retriever agent.
    """
    results = retriever.search_documents(query, top_k)
    return SearchResults(results=[SearchResult(text=result['text'], metadata=result['metadata']) for result in results])

class Document(BaseModel):
    text: str
    metadata: Dict[str, Any]

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    scores: List[float]

def create_index(documents: List[Document]):
    """Create a new FAISS index from documents"""
    try:
        global index
        
        if model is None:
            raise Exception("SentenceTransformer model not loaded")
        
        # Get document embeddings
        texts = [doc.text for doc in documents]
        embeddings = model.encode(texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        
        # Save index and documents
        faiss.write_index(index, "vector_store/index.faiss")
        with open("vector_store/documents.json", "w") as f:
            json.dump([doc.dict() for doc in documents], f)
            
    except Exception as e:
        logger.error(f"Error creating index: {str(e)}")
        raise

def load_index():
    """Load the FAISS index and documents from disk"""
    try:
        global index, documents
        
        # Load FAISS index if it exists
        if os.path.exists("vector_store/index.faiss"):
            index = faiss.read_index("vector_store/index.faiss")
        
        # Load documents if they exist
        if os.path.exists("vector_store/documents.json"):
            with open("vector_store/documents.json", "r") as f:
                documents = json.load(f)
                
    except Exception as e:
        logger.error(f"Error loading index: {str(e)}")
        raise
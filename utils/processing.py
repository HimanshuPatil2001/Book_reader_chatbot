import os
import pdfplumber  # Lighter alternative to PyMuPDF
import chromadb
import uuid
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv
import gc

# 🔐 Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Lazy loading for memory-intensive models
_model = None
_gemini = None
_collection = None
_sentence_transformer_ef = None

def get_model():
    """Lazy load the sentence transformer model with error handling"""
    global _model
    if _model is None:
        try:
            # Set NumPy to use compatible mode
            import numpy as np
            np.set_printoptions(legacy='1.13')
            
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not load sentence transformer model: {e}")
            print("Falling back to basic text processing...")
            _model = None
    return _model

def get_gemini():
    """Lazy load the Gemini model"""
    global _gemini
    if _gemini is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        try:
            configure(api_key=GEMINI_API_KEY)
            _gemini = GenerativeModel("models/gemini-2.0-flash")
        except Exception as e:
            print(f"Warning: Could not configure Gemini: {e}")
            raise e
    return _gemini

def get_collection():
    """Lazy load the ChromaDB collection with fallback"""
    global _collection, _sentence_transformer_ef
    if _collection is None:
        try:
            if _sentence_transformer_ef is None:
                _sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            chroma_client = chromadb.Client()
            _collection = chroma_client.create_collection(
                name="book_chunks",
                embedding_function=_sentence_transformer_ef
            )
        except Exception as e:
            print(f"Warning: Could not initialize ChromaDB: {e}")
            print("Falling back to basic text storage...")
            _collection = None
    return _collection

stored_chunks = []

def process_pdf(path):
    """Process PDF with memory management using pdfplumber"""
    global stored_chunks
    
    try:
        # Open and process PDF with pdfplumber (much lighter than PyMuPDF)
        with pdfplumber.open(path) as pdf:
            full_text = ""
            page_count = 0
            
            # Process pages with memory limits
            for page in pdf.pages:
                if page_count >= 50:  # Limit to 50 pages to prevent memory issues
                    break
                    
                try:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                    page_count += 1
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_count}: {e}")
                    continue
        
        # Limit total text length to prevent memory issues
        max_text_length = 500000  # Reduced to 500KB for 512MB RAM constraint
        if len(full_text) > max_text_length:
            full_text = full_text[:max_text_length]
        
        # Chunk text with reasonable limits
        chunk_size = 300  # Reduced chunk size for memory efficiency
        chunk_overlap = 50  # Reduced overlap
        chunks = []
        
        for i in range(0, len(full_text), chunk_size - chunk_overlap):
            chunk = full_text[i:i + chunk_size]
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Limit total chunks to prevent memory overflow
            if len(chunks) >= 500:  # Reduced from 1000 for 512MB RAM
                break
        
        stored_chunks = chunks
        
        # Add to ChromaDB with memory management (optional)
        try:
            collection = get_collection()
            if collection:
                ids = [str(uuid.uuid4()) for _ in chunks]
                collection.add(documents=chunks, ids=ids)
        except Exception as e:
            print(f"Warning: Could not add to ChromaDB: {e}")
            # Continue without ChromaDB if there's an issue
        
        # Force garbage collection
        gc.collect()
        
        return chunks
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        # Clean up on error
        gc.collect()
        raise e

def get_answer(query, chunks):
    """Get answer with error handling and memory management"""
    try:
        # Use stored chunks if available, otherwise search ChromaDB
        if chunks and len(chunks) > 0:
            context_chunks = chunks[:2]  # Reduced to 2 chunks for memory efficiency
        else:
            try:
                collection = get_collection()
                if collection:
                    results = collection.query(query_texts=[query], n_results=2)
                    context_chunks = results["documents"][0]
                else:
                    return "I'm sorry, I couldn't process your question. Please try uploading a PDF first."
            except Exception as e:
                print(f"Warning: ChromaDB search failed: {e}")
                return "I'm sorry, I couldn't process your question. Please try uploading a PDF first."
        
        # Limit context length to prevent memory issues
        context = "\n".join(context_chunks[:2])
        if len(context) > 3000:  # Reduced to 3KB for memory efficiency
            context = context[:3000]
        
        # Generate response with Gemini
        try:
            gemini_model = get_gemini()
            prompt = f"""
Only answer based on the following context.
If unsure or unrelated, say: "I don't know."

Context:
{context}

Question: {query}
Answer:
"""
            response = gemini_model.generate_content(prompt)
            
            # Clean up memory
            gc.collect()
            
            return response.text.strip()
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            # Fallback to basic response
            return f"Based on the document content, I found some relevant information: {context[:200]}... However, I couldn't generate a complete answer due to an error: {str(e)}"
        
    except Exception as e:
        print(f"Error generating answer: {e}")
        return f"I'm sorry, I encountered an error: {str(e)}"

def cleanup_memory():
    """Clean up memory and reset models"""
    global _model, _gemini, _collection, _sentence_transformer_ef, stored_chunks
    
    _model = None
    _gemini = None
    _collection = None
    _sentence_transformer_ef = None
    stored_chunks = []
    
    gc.collect()

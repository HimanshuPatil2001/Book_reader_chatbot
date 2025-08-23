import os
import fitz  # PyMuPDF
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
    """Lazy load the sentence transformer model"""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_gemini():
    """Lazy load the Gemini model"""
    global _gemini
    if _gemini is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        configure(api_key=GEMINI_API_KEY)
        _gemini = GenerativeModel("models/gemini-2.0-flash")
    return _gemini

def get_collection():
    """Lazy load the ChromaDB collection"""
    global _collection, _sentence_transformer_ef
    if _collection is None:
        if _sentence_transformer_ef is None:
            _sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        chroma_client = chromadb.Client()
        _collection = chroma_client.create_collection(
            name="book_chunks",
            embedding_function=_sentence_transformer_ef
        )
    return _collection

stored_chunks = []

def process_pdf(path):
    """Process PDF with memory management"""
    global stored_chunks
    
    try:
        # Open and process PDF
        doc = fitz.open(path)
        full_text = "\n".join(page.get_text() for page in doc)
        doc.close()  # Explicitly close to free memory
        
        # Chunk text with reasonable limits
        chunk_size = 500
        chunk_overlap = 100
        chunks = []
        
        # Limit total text length to prevent memory issues
        max_text_length = 1000000  # 1MB limit
        if len(full_text) > max_text_length:
            full_text = full_text[:max_text_length]
        
        for i in range(0, len(full_text), chunk_size - chunk_overlap):
            chunk = full_text[i:i + chunk_size]
            chunks.append(chunk)
            
            # Limit total chunks to prevent memory overflow
            if len(chunks) >= 1000:
                break
        
        stored_chunks = chunks
        
        # Add to ChromaDB with memory management
        try:
            collection = get_collection()
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
        if 'doc' in locals():
            doc.close()
        gc.collect()
        raise e

def get_answer(query, chunks):
    """Get answer with error handling and memory management"""
    try:
        # Use stored chunks if available, otherwise search ChromaDB
        if chunks and len(chunks) > 0:
            context_chunks = chunks[:3]  # Limit to top 3 chunks
        else:
            try:
                collection = get_collection()
                results = collection.query(query_texts=[query], n_results=3)
                context_chunks = results["documents"][0]
            except Exception as e:
                print(f"Warning: ChromaDB search failed: {e}")
                return "I'm sorry, I couldn't process your question. Please try uploading a PDF first."
        
        # Limit context length to prevent memory issues
        context = "\n".join(context_chunks[:3])
        if len(context) > 5000:  # Limit context to 5KB
            context = context[:5000]
        
        # Generate response with Gemini
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

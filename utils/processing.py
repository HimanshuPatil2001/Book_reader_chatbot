import os
import fitz  # PyMuPDF
import chromadb
import uuid
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv

# 🔐 Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 📌 Configure Gemini
configure(api_key=GEMINI_API_KEY)
gemini = GenerativeModel("models/gemini-2.0-flash")

# 🔎 Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 🧠 Use custom embedding function for Chroma
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# 🔁 Initialize Chroma client and collection
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(
    name="book_chunks",
    embedding_function=sentence_transformer_ef
)

stored_chunks = []

def process_pdf(path):
    global stored_chunks
    doc = fitz.open(path)
    full_text = "\n".join(page.get_text() for page in doc)

    # Chunk text
    chunk_size = 500
    chunk_overlap = 100
    chunks = []
    for i in range(0, len(full_text), chunk_size - chunk_overlap):
        chunk = full_text[i:i + chunk_size]
        chunks.append(chunk)

    stored_chunks = chunks

    # Add to ChromaDB
    ids = [str(uuid.uuid4()) for _ in chunks]
    collection.add(documents=chunks, ids=ids)

    return chunks

def get_answer(query, chunks):
    # Search ChromaDB for top 3 relevant chunks
    results = collection.query(query_texts=[query], n_results=3)
    context = "\n".join(results["documents"][0])

    # Gemini prompt
    prompt = f"""
Only answer based on the following context.
If unsure or unrelated, say: "I don't know."

Context:
{context}

Question: {query}
Answer:
"""
    response = gemini.generate_content(prompt)
    return response.text.strip()

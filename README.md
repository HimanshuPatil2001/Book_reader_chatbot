# 📚 Book Reader Chatbot

A powerful, AI-driven PDF chatbot that allows users to upload academic or technical PDFs and ask intelligent, context-aware questions about their content — all through an elegant and responsive web interface.

---

## 🚀 Features

- 📤 Upload and parse PDF documents  
- 💬 Ask contextual questions to the chatbot  
- ⚙️ Uses sentence transformers and vector search for document embeddings  
- 🧠 Integrates with LLMs (Google Gemini Pro or replaceable backend)  
- 🌙 Toggle between light/dark theme with modern gradients  
- 📈 Animated progress bar for upload status  
- 🪄 Refined UI with smooth transitions and typing indicators  
- 🔍 Displays most relevant lines from PDF on the side  

---

## 🛠 Tech Stack

| Frontend        | Backend        | ML/NLP & Tools              |
|----------------|----------------|-----------------------------|
| HTML, CSS (custom), JS | Flask (Python) | Sentence Transformers |
| Font Awesome Icons | REST API | FAISS / ChromaDB |
| Google Fonts | File Upload (PDF) | Google Gemini API* |

> *You can run the app without Gemini by modifying `processing.py`.

---

## 📁 Project Structure

```
📦 Book Reader Chatbot
├── app.py                  # Flask backend
├── utils/
│   └── processing.py       # PDF parsing, embeddings, and LLM logic
├── templates/
│   └── index.html          # Main UI page
├── static/
│   └── style.css           # All styling (including animations and themes)
├── uploads/                # Temporarily stored PDFs
├── .env                    # Your API key (not tracked by Git)
├── requirements.txt        # Python dependencies
└── .gitignore              # Ignore environment, .env, uploads, etc.
```

---

## 🧪 How It Works

1. **Upload PDF**  
   → PDF is parsed and broken down into clean text segments.

2. **Vector Embedding**  
   → Sentences are embedded using `sentence-transformers`.

3. **Vector Indexing**  
   → ChromaDB/FAISS indexes the vectors for efficient retrieval.

4. **Ask Questions**  
   → The most relevant chunk is retrieved and passed to LLM to generate response.

---

## 🔧 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/HimanshuPatil2001/Book_reader_chatbot.git
cd Book_reader_chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up `.env`

Create a `.env` file and paste:

```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

> Or comment out Gemini code if not using it.

### 5. Run the App

```bash
python app.py
```

Then open:  
👉 **http://127.0.0.1:5000/**

---

## 📌 Optional Improvements

- Switch from Gemini to local LLM (like Llama 3)
- Save chat history per user
- Authenticated sessions
- PDF highlight mapping to answers

---

## 📃 License

MIT License — Free to use and modify

---

## 🙋‍♂️ Author

**Himanshu Patil**  
📎 [GitHub Profile](https://github.com/HimanshuPatil2001)
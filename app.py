from flask import Flask, render_template, request, jsonify
from utils.processing import process_pdf, get_answer
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global chunks storage with memory limit
chunks = []
MAX_CHUNKS = 1000  # Limit memory usage

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global chunks
    try:
        file = request.files['pdf']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Process PDF and limit memory usage
            new_chunks = process_pdf(filepath)
            chunks = new_chunks[:MAX_CHUNKS]  # Limit chunks to prevent memory overflow
            
            # Clean up old file
            if os.path.exists(filepath):
                os.remove(filepath)
                
            return jsonify({"success": True, "chunks_processed": len(chunks)})
        return jsonify({"success": False, "error": "No file provided"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/ask', methods=['POST'])
def ask():
    try:
        query = request.json['query']
        if not chunks:
            return jsonify({"answer": "Please upload a PDF first."})
        
        answer = get_answer(query, chunks)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error processing query: {str(e)}"})

@app.route('/health')
def health():
    """Health check endpoint for deployment platforms"""
    return jsonify({"status": "healthy", "chunks_loaded": len(chunks)})

if __name__ == '__main__':
    # Production configuration - disable debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    )

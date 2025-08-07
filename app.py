from flask import Flask, render_template, request, jsonify
from utils.processing import process_pdf, get_answer
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

chunks = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global chunks
    file = request.files['pdf']
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        chunks = process_pdf(filepath)
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/ask', methods=['POST'])
def ask():
    query = request.json['query']
    answer = get_answer(query, chunks)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)

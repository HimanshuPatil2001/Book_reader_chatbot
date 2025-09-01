# Book Reader Chatbot

A Flask-based chatbot that can read PDF documents and answer questions about their content using AI.

## Demo

![Tutorial](./assets/tutorial.gif)

## Features

- PDF upload and processing
- AI-powered question answering using Google Gemini
- Vector search with ChromaDB
- Modern web interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Book_reader_chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create a .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

## Development

To run in development mode:
```bash
export FLASK_DEBUG=True
python app.py
```

## Production Deployment

### Option 1: Using Gunicorn (Recommended)

1. Make the deployment script executable:
```bash
chmod +x deploy.sh
```

2. Run the deployment script:
```bash
./deploy.sh
```

### Option 2: Manual Gunicorn

```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
gunicorn -c gunicorn.conf.py wsgi:app
```

### Option 3: Using WSGI directly

```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
python wsgi.py
```

## Environment Variables

- `FLASK_ENV`: Set to 'production' for production deployment
- `FLASK_DEBUG`: Set to 'False' for production deployment
- `GEMINI_API_KEY`: Your Google Gemini API key
- `PORT`: Port number (default: 5000)
- `HOST`: Host address (default: 0.0.0.0)

## Memory Management

This application has been optimized to prevent out-of-memory (OOM) errors:

- **Lazy Loading**: AI models are loaded only when needed
- **Memory Limits**: PDF processing is limited to prevent memory overflow
- **Garbage Collection**: Automatic memory cleanup after operations
- **Chunk Limits**: Maximum 1000 text chunks stored in memory
- **File Size Limits**: PDFs are limited to 1MB of text content

## Troubleshooting

### Out of Memory Errors

If you encounter OOM errors:

1. **Ensure debug mode is disabled**:
   ```bash
   export FLASK_DEBUG=False
   ```

2. **Use Gunicorn instead of Flask development server**:
   ```bash
   gunicorn -c gunicorn.conf.py wsgi:app
   ```

3. **Check available memory**:
   ```bash
   free -h
   ```

4. **Reduce worker processes** (edit `gunicorn.conf.py`):
   ```python
   workers = 2  # Reduce from default
   ```

### Common Issues

- **Port already in use**: Change the PORT environment variable
- **Permission denied**: Ensure the uploads directory is writable
- **API key errors**: Verify your GEMINI_API_KEY is set correctly

## API Endpoints

- `GET /`: Main interface
- `POST /upload`: Upload PDF file
- `POST /ask`: Ask a question about the uploaded PDF
- `GET /health`: Health check endpoint

## File Structure

```
Book_reader_chatbot/
├── app.py              # Main Flask application
├── wsgi.py             # WSGI entry point for production
├── gunicorn.conf.py    # Gunicorn configuration
├── deploy.sh           # Deployment script
├── requirements.txt    # Python dependencies
├── static/             # Static files (CSS, JS)
├── templates/          # HTML templates
├── utils/              # Utility modules
└── uploads/            # PDF upload directory
```

## Performance Tips

1. **Use Gunicorn** instead of Flask development server
2. **Limit PDF sizes** to prevent memory issues
3. **Monitor memory usage** during deployment
4. **Use health checks** to monitor application status

## Security Notes

- Debug mode is automatically disabled in production
- File uploads are limited and cleaned up after processing
- Environment variables are used for sensitive configuration
- Input validation and error handling are implemented

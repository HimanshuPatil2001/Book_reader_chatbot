#!/bin/bash

# Production deployment script for Book Reader Chatbot
echo "🚀 Starting production deployment..."

# Set production environment variables
export FLASK_ENV=production
export FLASK_DEBUG=False
export PYTHONUNBUFFERED=1

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if Gunicorn is available
if command -v gunicorn &> /dev/null; then
    echo "🔄 Starting with Gunicorn (production WSGI server)..."
    gunicorn -c gunicorn.conf.py wsgi:app
else
    echo "⚠️  Gunicorn not found, falling back to Flask development server..."
    echo "⚠️  WARNING: This is not recommended for production!"
    python wsgi.py
fi

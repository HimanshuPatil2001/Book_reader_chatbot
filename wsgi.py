#!/usr/bin/env python3
"""
WSGI entry point for production deployment
This file is used by production WSGI servers like Gunicorn or uWSGI
"""

import os
from app import app

# Set production environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

if __name__ == "__main__":
    # Production configuration
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(
        host=host,
        port=port,
        debug=False,
        threaded=True
    )

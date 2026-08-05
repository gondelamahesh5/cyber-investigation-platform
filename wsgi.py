"""
WSGI entry point for production deployment
"""
import os
from app import create_app

# Create application instance
app = create_app(os.getenv('FLASK_CONFIG', 'production'))

if __name__ == '__main__':
    # This is only used when running locally
    # For production, use Gunicorn or uWSGI
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
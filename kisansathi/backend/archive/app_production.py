#!/usr/bin/env python3
"""
KisanSathi - Production Minimal Backend
Lightweight version for Render deployment
"""

import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from dotenv import load_dotenv
import logging
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'kisansathi_secret_key_2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# MongoDB
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB = os.getenv('MONGODB_DATABASE', 'kisansathi')

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGODB_DB]
    client.admin.command('ping')
    logger.info(f"✅ Connected to MongoDB: {MONGODB_DB}")
except Exception as e:
    logger.warning(f"⚠️ MongoDB connection failed: {e}")
    db = None

# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'KisanSathi Backend API (Production)',
        'version': '5.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'status': '/api/status',
            'auth': '/api/auth/*',
            'recommendations': '/api/recommendations/*'
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'kisansathi-backend'
    }), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    """Status endpoint"""
    db_status = 'connected' if db is not None else 'disconnected'
    return jsonify({
        'status': 'running',
        'database': db_status,
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register user"""
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        if not db:
            return jsonify({'error': 'Database not available'}), 503
        
        if db['users'].find_one({'email': data['email']}):
            return jsonify({'error': 'User already exists'}), 409
        
        result = db['users'].insert_one({
            'email': data['email'],
            'password': data['password'],
            'created_at': datetime.now()
        })
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        if not db:
            return jsonify({'error': 'Database not available'}), 503
        
        user = db['users'].find_one({'email': data['email']})
        if not user or user['password'] != data['password']:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            'access_token': access_token,
            'user_id': str(user['_id']),
            'email': user['email']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PLACEHOLDER ENDPOINTS
# ============================================================================

@app.route('/api/recommendations/crop', methods=['POST'])
def crop_recommendation():
    """Crop recommendation"""
    return jsonify({
        'recommendations': [
            {'crop': 'Rice', 'confidence': 0.85},
            {'crop': 'Wheat', 'confidence': 0.75},
            {'crop': 'Corn', 'confidence': 0.65}
        ]
    }), 200

@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    """Chatbot message"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        return jsonify({
            'response': f'Echo: {message}',
            'status': 'ok'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """Dashboard stats"""
    return jsonify({
        'performance': {
            'uptime_seconds': 3600,
            'total_requests': 1000,
            'total_errors': 5,
            'error_rate': 0.5,
            'avg_response_time_ms': 150,
            'requests_per_minute': 16.67
        },
        'system': {
            'cpu_percent': 25.5,
            'memory_percent': 45.2,
            'memory_used_mb': 2048,
            'memory_total_mb': 4096,
            'disk_percent': 60.0,
            'disk_used_gb': 300,
            'disk_total_gb': 500
        }
    }), 200

@app.route('/api/dashboard/alerts', methods=['GET'])
def dashboard_alerts():
    """Dashboard alerts"""
    return jsonify({'alerts': []}), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting KisanSathi Backend (Production)")
    logger.info(f"✅ All endpoints ready!")
    app.run(host='0.0.0.0', port=port, debug=False)

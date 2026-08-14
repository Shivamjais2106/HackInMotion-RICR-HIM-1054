"""
Health and status probes.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import jsonify
from datetime import datetime
from extensions import limiter
from database import redis_manager

import logging

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/api/health', methods=['GET'])
@limiter.limit("100 per hour")
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'MongoDB',
        'version': '4.0.0'
    }), 200

@health_bp.route('/api/status', methods=['GET'])
@limiter.limit("100 per hour")
def status():
    """Get application status"""
    redis_status = 'connected' if redis_manager and redis_manager.connected else 'disconnected'
    
    return jsonify({
        'app': 'KisanSathi Backend (Enhanced)',
        'version': '5.0.0',
        'environment': 'production',
        'database': 'MongoDB',
        'cache': 'Redis',
        'redis_status': redis_status,
        'features': [
            'JWT Authentication',
            'Rate Limiting',
            'Redis Caching',
            'Admin Management',
            'AI Chatbot',
            'ML Models',
            'File Handling',
            'Weather Integration'
        ],
        'timestamp': datetime.now().isoformat()
    }), 200

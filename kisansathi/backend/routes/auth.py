"""
Registration, login and profile (JWT).

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

import bcrypt

from flask import Blueprint
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from bson.objectid import ObjectId
from extensions import limiter
from database import db
from decorators import error_handler, validate_json

import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per hour")
@error_handler
@validate_json('name', 'email', 'mobile', 'password', 'agriculture_type')
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Check if user already exists
    if db['users'].find_one({'$or': [{'email': data['email']}, {'mobile': data['mobile']}]}):
        return jsonify({'error': 'User already exists'}), 400
    
    hashed_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_doc = {
        'name': data['name'],
        'email': data['email'],
        'mobile': data['mobile'],
        'password': hashed_pw,
        'agriculture_type': data['agriculture_type'],
        'location': data.get('location', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    result = db['users'].insert_one(user_doc)
    
    logger.info(f"New user registered: {data['name']} ({data['mobile']})")
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': str(result.inserted_id)
    }), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per hour")
@error_handler
@validate_json('mobile', 'password')
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    mobile = data['mobile']
    password = data['password']

    # Find user by mobile
    user = db['users'].find_one({'mobile': mobile})

    if not user:
        logger.warning(f"Failed login attempt for mobile: {mobile}")
        return jsonify({'error': 'Invalid credentials'}), 401

    # Verify password (support both bcrypt-hashed and legacy plain-text passwords)
    password_bytes = password.encode('utf-8')
    stored_pw = user['password']
    if stored_pw.startswith('$2b$') or stored_pw.startswith('$2a$'):
        # bcrypt-hashed password
        if not bcrypt.checkpw(password_bytes, stored_pw.encode('utf-8')):
            logger.warning(f"Failed login attempt for mobile: {mobile}")
            return jsonify({'error': 'Invalid credentials'}), 401
    else:
        # Legacy plain-text password — verify and re-hash on the fly
        if stored_pw != password:
            logger.warning(f"Failed login attempt for mobile: {mobile}")
            return jsonify({'error': 'Invalid credentials'}), 401
        # Upgrade to bcrypt on next successful login
        new_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
        db['users'].update_one({'mobile': mobile}, {'$set': {'password': new_hash}})
    
    # Create JWT token
    access_token = create_access_token(identity=str(user['_id']))
    
    logger.info(f"User logged in: {user['name']} ({mobile})")
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user_id': str(user['_id']),
        'name': user['name'],
        'mobile': mobile,
        'token_type': 'Bearer'
    }), 200

@auth_bp.route('/api/auth/profile', methods=['GET'])
@jwt_required()
@error_handler
def get_profile():
    """Get current user profile"""
    user_id = get_jwt_identity()
    
    try:
        user = db['users'].find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user['_id'] = str(user['_id'])
        del user['password']  # Don't send password
        
        return jsonify({
            'user': user
        }), 200
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return jsonify({'error': 'Invalid user ID'}), 400

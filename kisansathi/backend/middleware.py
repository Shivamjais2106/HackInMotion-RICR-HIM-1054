#!/usr/bin/env python3
"""
Middleware for KisanSathi Backend
Handles authentication, validation, error handling, logging, and rate limiting
"""

from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# ERROR HANDLING MIDDLEWARE
# ============================================================================

<<<<<<< HEAD

def error_handler(f):
    """
    Decorator to handle errors with proper logging and response formatting

=======
def error_handler(f):
    """
    Decorator to handle errors with proper logging and response formatting
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        @app.route('/api/endpoint')
        @error_handler
        def endpoint():
            return jsonify({'data': 'value'}), 200
    """
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error in {f.__name__}: {str(e)}")
<<<<<<< HEAD
            return jsonify({"error": "Validation error", "message": str(e)}), 400
        except KeyError as e:
            logger.warning(f"Missing key in {f.__name__}: {str(e)}")
            return jsonify({"error": "Missing required field", "field": str(e)}), 400
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({"error": "Internal server error", "message": str(e)}), 500

    return decorated


=======
            return jsonify({
                'error': 'Validation error',
                'message': str(e)
            }), 400
        except KeyError as e:
            logger.warning(f"Missing key in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Missing required field',
                'field': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
    return decorated

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# ============================================================================
# JSON VALIDATION MIDDLEWARE
# ============================================================================

<<<<<<< HEAD

def validate_json(*expected_args):
    """
    Decorator to validate JSON request data

=======
def validate_json(*expected_args):
    """
    Decorator to validate JSON request data
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_json('field1', 'field2')
        def endpoint():
            data = request.get_json()
            return jsonify({'data': data}), 200
    """
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Check if request has JSON
            if not request.is_json:
<<<<<<< HEAD
                return jsonify({"error": "Request must be JSON", "content_type": request.content_type}), 400

            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body cannot be empty"}), 400

            # Check for missing fields
            missing = [arg for arg in expected_args if arg not in data]
            if missing:
                return jsonify({"error": "Missing required fields", "missing_fields": missing}), 400

            return f(*args, **kwargs)

        return decorated

    return decorator


=======
                return jsonify({
                    'error': 'Request must be JSON',
                    'content_type': request.content_type
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body cannot be empty'}), 400
            
            # Check for missing fields
            missing = [arg for arg in expected_args if arg not in data]
            if missing:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing_fields': missing
                }), 400
            
            return f(*args, **kwargs)
        return decorated
    return decorator

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# ============================================================================
# INPUT VALIDATION MIDDLEWARE
# ============================================================================

<<<<<<< HEAD

def validate_email(email):
    """Validate email format"""
    pattern = r"^[^@]+@[^@]+\.[^@]+$"
    return re.match(pattern, email) is not None


def validate_mobile(mobile):
    """Validate mobile number (10 digits)"""
    pattern = r"^\d{10}$"
    return re.match(pattern, str(mobile)) is not None


=======
def validate_email(email):
    """Validate email format"""
    pattern = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(pattern, email) is not None

def validate_mobile(mobile):
    """Validate mobile number (10 digits)"""
    pattern = r'^\d{10}$'
    return re.match(pattern, str(mobile)) is not None

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
<<<<<<< HEAD

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain number"

    return True, "Password is valid"


def validate_input(data, rules):
    """
    Validate input data against rules

=======
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain number"
    
    return True, "Password is valid"

def validate_input(data, rules):
    """
    Validate input data against rules
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        rules = {
            'email': {'type': 'email', 'required': True},
            'mobile': {'type': 'mobile', 'required': True},
            'password': {'type': 'password', 'required': True}
        }
        errors = validate_input(data, rules)
        if errors:
            return jsonify({'errors': errors}), 400
    """
    errors = {}
<<<<<<< HEAD

    for field, rule in rules.items():
        if rule.get("required") and field not in data:
            errors[field] = f"{field} is required"
            continue

        if field not in data:
            continue

        value = data[field]
        field_type = rule.get("type")

        if field_type == "email":
            if not validate_email(value):
                errors[field] = "Invalid email format"

        elif field_type == "mobile":
            if not validate_mobile(value):
                errors[field] = "Mobile must be 10 digits"

        elif field_type == "password":
            is_valid, message = validate_password(value)
            if not is_valid:
                errors[field] = message

        elif field_type == "string":
            if not isinstance(value, str):
                errors[field] = f"{field} must be string"

        elif field_type == "number":
            if not isinstance(value, (int, float)):
                errors[field] = f"{field} must be number"

    return errors if errors else None


=======
    
    for field, rule in rules.items():
        if rule.get('required') and field not in data:
            errors[field] = f"{field} is required"
            continue
        
        if field not in data:
            continue
        
        value = data[field]
        field_type = rule.get('type')
        
        if field_type == 'email':
            if not validate_email(value):
                errors[field] = "Invalid email format"
        
        elif field_type == 'mobile':
            if not validate_mobile(value):
                errors[field] = "Mobile must be 10 digits"
        
        elif field_type == 'password':
            is_valid, message = validate_password(value)
            if not is_valid:
                errors[field] = message
        
        elif field_type == 'string':
            if not isinstance(value, str):
                errors[field] = f"{field} must be string"
        
        elif field_type == 'number':
            if not isinstance(value, (int, float)):
                errors[field] = f"{field} must be number"
    
    return errors if errors else None

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# ============================================================================
# AUTHENTICATION MIDDLEWARE
# ============================================================================

<<<<<<< HEAD

def require_auth(f):
    """
    Decorator to require JWT authentication

=======
def require_auth(f):
    """
    Decorator to require JWT authentication
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        @app.route('/api/protected')
        @jwt_required()
        @require_auth
        def protected():
            user_id = get_jwt_identity()
            return jsonify({'user_id': user_id}), 200
    """
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            if not user_id:
<<<<<<< HEAD
                return jsonify({"error": "User not found"}), 401

=======
                return jsonify({'error': 'User not found'}), 401
            
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
            logger.info(f"Authenticated user: {user_id}")
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
<<<<<<< HEAD
            return jsonify({"error": "Authentication failed"}), 401

    return decorated


def check_admin(db, group_id):
    """
    Check if current user is admin of group

=======
            return jsonify({'error': 'Authentication failed'}), 401
    return decorated

def check_admin(db, group_id):
    """
    Check if current user is admin of group
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        if not check_admin(db, group_id):
            return jsonify({'error': 'Only admins can perform this action'}), 403
    """
    from bson import ObjectId
<<<<<<< HEAD

    user_id = get_jwt_identity()
    group = db["groups"].find_one({"_id": ObjectId(group_id), "admins": ObjectId(user_id)})

    return group is not None


def check_ownership(db, message_id):
    """
    Check if current user owns message

=======
    
    user_id = get_jwt_identity()
    group = db['groups'].find_one({
        '_id': ObjectId(group_id),
        'admins': ObjectId(user_id)
    })
    
    return group is not None

def check_ownership(db, message_id):
    """
    Check if current user owns message
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        user_id = get_jwt_identity()
        if not check_ownership(db, message_id):
            return jsonify({'error': 'Can only delete own messages'}), 403
    """
    from bson import ObjectId
<<<<<<< HEAD

    user_id = get_jwt_identity()
    message = db["messages"].find_one({"_id": ObjectId(message_id), "sender_id": ObjectId(user_id)})

    return message is not None


=======
    
    user_id = get_jwt_identity()
    message = db['messages'].find_one({
        '_id': ObjectId(message_id),
        'sender_id': ObjectId(user_id)
    })
    
    return message is not None

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# ============================================================================
# LOGGING MIDDLEWARE
# ============================================================================

<<<<<<< HEAD

def log_request(f):
    """
    Decorator to log all requests

=======
def log_request(f):
    """
    Decorator to log all requests
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        @app.route('/api/endpoint')
        @log_request
        def endpoint():
            return jsonify({'data': 'value'}), 200
    """
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.info(f"Request: {request.method} {request.path}")
        logger.info(f"Remote Address: {request.remote_addr}")
<<<<<<< HEAD

        if request.is_json:
            logger.debug(f"Request Body: {request.get_json()}")

        result = f(*args, **kwargs)

=======
        
        if request.is_json:
            logger.debug(f"Request Body: {request.get_json()}")
        
        result = f(*args, **kwargs)
        
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        if isinstance(result, tuple):
            status_code = result[1]
        else:
            status_code = 200
<<<<<<< HEAD

        logger.info(f"Response: {status_code}")
        return result

    return decorated


def log_action(action, resource, user_id, status, db):
    """
    Log user action to audit trail

=======
        
        logger.info(f"Response: {status_code}")
        return result
    return decorated

def log_action(action, resource, user_id, status, db):
    """
    Log user action to audit trail
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        log_action('create_group', group_id, user_id, 'success', db)
    """
    try:
        audit_log = {
<<<<<<< HEAD
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "ip_address": request.remote_addr,
        }

        db["audit_logs"].insert_one(audit_log)
=======
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr
        }
        
        db['audit_logs'].insert_one(audit_log)
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        logger.info(f"Audit: {action} on {resource} by {user_id} - {status}")
    except Exception as e:
        logger.error(f"Failed to log action: {str(e)}")

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# ============================================================================
# CACHING MIDDLEWARE
# ============================================================================

<<<<<<< HEAD

def cache_response(timeout=300):
    """
    Decorator to cache response

=======
def cache_response(timeout=300):
    """
    Decorator to cache response
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        @app.route('/api/endpoint')
        @cache_response(timeout=600)
        def endpoint():
            return jsonify({'data': 'value'}), 200
    """
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask_caching import Cache
<<<<<<< HEAD

            cache = Cache(app=None, config={"CACHE_TYPE": "simple"})

            cache_key = f"{request.path}:{request.args}"
            cached = cache.get(cache_key)

            if cached:
                logger.debug(f"Cache hit: {cache_key}")
                return cached

            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            logger.debug(f"Cache set: {cache_key}")

            return result

        return decorated

    return decorator


=======
            cache = Cache(app=None, config={'CACHE_TYPE': 'simple'})
            
            cache_key = f"{request.path}:{request.args}"
            cached = cache.get(cache_key)
            
            if cached:
                logger.debug(f"Cache hit: {cache_key}")
                return cached
            
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            logger.debug(f"Cache set: {cache_key}")
            
            return result
        return decorated
    return decorator

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# ============================================================================
# RATE LIMITING MIDDLEWARE
# ============================================================================

<<<<<<< HEAD

def rate_limit_by_user(limit="10 per minute"):
    """
    Decorator to rate limit by user

=======
def rate_limit_by_user(limit="10 per minute"):
    """
    Decorator to rate limit by user
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        @app.route('/api/endpoint')
        @rate_limit_by_user(limit="5 per minute")
        def endpoint():
            return jsonify({'data': 'value'}), 200
    """
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask_jwt_extended import get_jwt_identity
<<<<<<< HEAD

=======
            
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
            try:
                user_id = get_jwt_identity()
                # Rate limiting logic would go here
                # Using Flask-Limiter in main app
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Rate limiting error: {str(e)}")
                return f(*args, **kwargs)
<<<<<<< HEAD

        return decorated

    return decorator


=======
        return decorated
    return decorator

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# ============================================================================
# RESPONSE FORMATTING MIDDLEWARE
# ============================================================================

<<<<<<< HEAD

def format_response(data, message="Success", status_code=200):
    """
    Format API response consistently

=======
def format_response(data, message="Success", status_code=200):
    """
    Format API response consistently
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        return format_response(
            data={'user_id': '123'},
            message='User created',
            status_code=201
        )
    """
<<<<<<< HEAD
    response = {"message": message, "data": data, "timestamp": datetime.now().isoformat()}

    return jsonify(response), status_code


def format_error(error, status_code=400, details=None):
    """
    Format error response consistently

=======
    response = {
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(response), status_code

def format_error(error, status_code=400, details=None):
    """
    Format error response consistently
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        return format_error(
            error='Invalid input',
            status_code=400,
            details={'field': 'email', 'reason': 'Invalid format'}
        )
    """
<<<<<<< HEAD
    response = {"error": error, "timestamp": datetime.now().isoformat()}

    if details:
        response["details"] = details

    return jsonify(response), status_code


=======
    response = {
        'error': error,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

<<<<<<< HEAD

def setup_cors(app):
    """
    Setup CORS for the application

=======
def setup_cors(app):
    """
    Setup CORS for the application
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        setup_cors(app)
    """
    from flask_cors import CORS
<<<<<<< HEAD

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:8080", "http://localhost:3000"],
                "methods": ["GET", "POST", "DELETE", "PUT", "PATCH"],
                "allow_headers": ["Content-Type", "Authorization"],
                "max_age": 3600,
            }
        },
    )

    logger.info("CORS configured")


=======
    
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080", "http://localhost:3000"],
            "methods": ["GET", "POST", "DELETE", "PUT", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"],
            "max_age": 3600
        }
    })
    
    logger.info("CORS configured")

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# ============================================================================
# SECURITY MIDDLEWARE
# ============================================================================

<<<<<<< HEAD

def add_security_headers(app):
    """
    Add security headers to all responses

    Usage:
        add_security_headers(app)
    """

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

    logger.info("Security headers configured")


=======
def add_security_headers(app):
    """
    Add security headers to all responses
    
    Usage:
        add_security_headers(app)
    """
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    
    logger.info("Security headers configured")

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
# ============================================================================
# MIDDLEWARE INITIALIZATION
# ============================================================================

<<<<<<< HEAD

def init_middleware(app):
    """
    Initialize all middleware for the application

=======
def init_middleware(app):
    """
    Initialize all middleware for the application
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    Usage:
        init_middleware(app)
    """
    setup_cors(app)
    add_security_headers(app)
    logger.info("All middleware initialized")

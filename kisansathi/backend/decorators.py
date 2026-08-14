"""
Cross-cutting decorators used by the KisanSathi route blueprints.

Moved out of the single-file app unchanged so every blueprint keeps the same
error envelope, validation messages and cache keys the frontend already expects.
"""

import logging
from functools import wraps

from flask import jsonify, request

from database import redis_manager

logger = logging.getLogger(__name__)


def error_handler(f):
    """Decorator to handle errors with proper logging"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Internal server error',
                'message': str(e),
                'endpoint': f.__name__
            }), 500
    return decorated


def validate_json(*expected_args):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body must be JSON'}), 400

            missing = [arg for arg in expected_args if arg not in data]
            if missing:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing_fields': missing
                }), 400

            return f(*args, **kwargs)
        return decorated
    return decorator


def redis_cache(expire=3600):
    """Decorator to cache GET requests in Redis"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not redis_manager or not redis_manager.connected:
                return f(*args, **kwargs)

            # Create cache key from function name and args
            cache_key = f"cache:{f.__name__}:{request.path}:{request.query_string.decode()}"

            # Try to get from cache
            cached = redis_manager.get(cache_key)
            if cached:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached

            # Call function and cache result
            result = f(*args, **kwargs)

            # Cache successful responses
            if isinstance(result, tuple) and result[1] == 200:
                redis_manager.set(cache_key, result[0], expire=expire)
                logger.debug(f"Cache SET: {cache_key}")

            return result
        return decorated
    return decorator

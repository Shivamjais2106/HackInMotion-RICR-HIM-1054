"""
Redis cache inspection and invalidation.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import jsonify
from extensions import limiter
from database import redis_manager
from decorators import error_handler

import logging

logger = logging.getLogger(__name__)

cache_admin_bp = Blueprint("cache_admin", __name__)


@cache_admin_bp.route("/api/cache/stats", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
def cache_stats():
    """Get Redis cache statistics"""
    if not redis_manager or not redis_manager.connected:
        return jsonify({"status": "disconnected", "message": "Redis is not connected"}), 503

    stats = redis_manager.get_stats()
    return jsonify(stats), 200


@cache_admin_bp.route("/api/cache/clear", methods=["POST"])
@limiter.limit("5 per hour")
@error_handler
def cache_clear():
    """Clear all Redis cache"""
    if not redis_manager or not redis_manager.connected:
        return jsonify({"error": "Redis is not connected"}), 503

    redis_manager.flush_all()
    logger.info("Redis cache cleared by user")

    return jsonify({"message": "Cache cleared successfully"}), 200


@cache_admin_bp.route("/api/cache/clear/<pattern>", methods=["POST"])
@limiter.limit("10 per hour")
@error_handler
def cache_clear_pattern(pattern):
    """Clear cache by pattern"""
    if not redis_manager or not redis_manager.connected:
        return jsonify({"error": "Redis is not connected"}), 503

    count = redis_manager.clear_pattern(pattern)
    logger.info(f"Cleared {count} cache entries matching pattern: {pattern}")

    return jsonify({"message": f"Cleared {count} cache entries", "pattern": pattern}), 200

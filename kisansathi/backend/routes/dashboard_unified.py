"""
Single-call unified farmer dashboard.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from decorators import error_handler

import logging

logger = logging.getLogger(__name__)

dashboard_unified_bp = Blueprint('dashboard_unified', __name__)


@dashboard_unified_bp.route('/api/dashboard/unified', methods=['GET'])
@jwt_required()
@error_handler
def unified_dashboard():
    """
    Unified dashboard — returns farm profile, weather, irrigation decision,
    risk alerts, market prices for farmer's crops, and today's priority actions.
    Requirement 6: Unified Farmer Dashboard
    """
    try:
        from utils.dashboard_builder import build_dashboard
        user_id = get_jwt_identity()
        data = build_dashboard(db, user_id)
        return jsonify({'success': True, **data}), 200
    except Exception as e:
        logger.error(f"Unified dashboard error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

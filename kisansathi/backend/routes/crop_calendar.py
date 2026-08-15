"""
Crop calendar, months and seasons.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import jsonify
from datetime import datetime
from extensions import limiter, cache
from decorators import error_handler
from integrations import get_crop_calendar, get_crops_for_month, get_crop_details, get_seasonal_activities

import logging

logger = logging.getLogger(__name__)

crop_calendar_bp = Blueprint("crop_calendar", __name__)


@crop_calendar_bp.route("/api/crop-calendar", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def crop_calendar():
    """Get seasonal crop calendar"""
    try:
        calendar = get_crop_calendar()

        logger.info("Crop calendar retrieved")

        return jsonify({"calendar": calendar, "timestamp": datetime.now().isoformat()}), 200
    except Exception as e:
        logger.error(f"Error getting crop calendar: {e}")
        return jsonify({"error": f"Calendar retrieval failed: {str(e)}"}), 500


@crop_calendar_bp.route("/api/months", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def get_months():
    """Get list of all months for crop selection"""
    try:
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        logger.info("Months list retrieved")

        return jsonify(
            {"success": True, "months": months, "total": len(months), "timestamp": datetime.now().isoformat()}
        ), 200
    except Exception as e:
        logger.error(f"Error getting months: {e}")
        return jsonify({"error": f"Failed to get months: {str(e)}"}), 500


@crop_calendar_bp.route("/api/crop-calendar/month/<month>", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def crops_for_month(month):
    """Get crops recommended for a specific month"""
    try:
        crops = get_crops_for_month(month)

        logger.info(f"Crops retrieved for {month}")

        return jsonify(
            {"month": month, "crops": crops, "total": len(crops), "timestamp": datetime.now().isoformat()}
        ), 200
    except Exception as e:
        logger.error(f"Error getting crops for month: {e}")
        return jsonify({"error": f"Failed to get crops: {str(e)}"}), 500


@crop_calendar_bp.route("/api/crop-calendar/crop/<crop_name>", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
def crop_info(crop_name):
    """Get detailed information about a specific crop"""
    try:
        details = get_crop_details(crop_name)

        # try case-insensitive if not found
        if not details:
            details = get_crop_details(crop_name.capitalize())
        if not details:
            details = get_crop_details(crop_name.lower())
        if not details:
            details = get_crop_details(crop_name.upper())

        if details is None or (isinstance(details, dict) and not details):
            return jsonify({"error": "Crop not found"}), 404

        logger.info(f"Crop details retrieved for {crop_name}")

        return jsonify({"crop": crop_name, "details": details, "timestamp": datetime.now().isoformat()}), 200
    except Exception as e:
        logger.error(f"Error getting crop details: {e}")
        return jsonify({"error": f"Failed to get crop details: {str(e)}"}), 500


@crop_calendar_bp.route("/api/crop-calendar/season/<season>", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def seasonal_activities(season):
    """Get farming activities for a season"""
    try:
        activities = get_seasonal_activities(season)

        logger.info(f"Seasonal activities retrieved for {season}")

        return jsonify({"season": season, "activities": activities, "timestamp": datetime.now().isoformat()}), 200
    except Exception as e:
        logger.error(f"Error getting seasonal activities: {e}")
        return jsonify({"error": f"Failed to get activities: {str(e)}"}), 500

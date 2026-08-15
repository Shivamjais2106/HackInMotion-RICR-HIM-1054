"""
Pest identification and per-crop pest lists.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import jsonify
from datetime import datetime
from extensions import limiter, cache
from decorators import error_handler
from integrations import identify_pest, get_all_pests, get_pests_for_crop

import logging

logger = logging.getLogger(__name__)

pest_bp = Blueprint("pest", __name__)


@pest_bp.route("/api/pest/identify/<pest_name>", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
def pest_identify(pest_name):
    """Identify pest and get management strategies"""
    try:
        pest_info = identify_pest(pest_name)

        # try case-insensitive variants if not found or empty
        if not pest_info:
            pest_info = identify_pest(pest_name.capitalize())
        if not pest_info:
            pest_info = identify_pest(pest_name.title())
        if not pest_info:
            pest_info = identify_pest(pest_name.lower())
        # strip trailing 's' for plural (aphids -> aphid)
        if not pest_info and pest_name.lower().endswith("s"):
            pest_info = identify_pest(pest_name[:-1].capitalize())

        if pest_info is None or (isinstance(pest_info, dict) and not pest_info):
            return jsonify({"error": "Pest not found"}), 404

        logger.info(f"Pest information retrieved for {pest_name}")

        return jsonify({"pest": pest_name, "information": pest_info, "timestamp": datetime.now().isoformat()}), 200
    except Exception as e:
        logger.error(f"Error identifying pest: {e}")
        return jsonify({"error": f"Failed to identify pest: {str(e)}"}), 500


@pest_bp.route("/api/pest/all", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def all_pests():
    """Get list of all managed pests"""
    try:
        pests = get_all_pests()

        logger.info("All pests list retrieved")

        return jsonify({"pests": pests, "total": len(pests), "timestamp": datetime.now().isoformat()}), 200
    except Exception as e:
        logger.error(f"Error getting pests list: {e}")
        return jsonify({"error": f"Failed to get pests: {str(e)}"}), 500


@pest_bp.route("/api/pest/crop/<crop_name>", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def pests_for_crop(crop_name):
    """Get pests that affect a specific crop"""
    try:
        pests = get_pests_for_crop(crop_name)

        logger.info(f"Pests retrieved for {crop_name}")

        return jsonify(
            {"crop": crop_name, "pests": pests, "total": len(pests), "timestamp": datetime.now().isoformat()}
        ), 200
    except Exception as e:
        logger.error(f"Error getting pests for crop: {e}")
        return jsonify({"error": f"Failed to get pests: {str(e)}"}), 500

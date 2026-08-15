"""
Soil analysis and reference lists.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import request, jsonify
from extensions import limiter
from decorators import error_handler
from integrations import analyze_soil, get_soil_types, get_crop_types, get_fertilizer_types

import logging

logger = logging.getLogger(__name__)

soil_bp = Blueprint("soil", __name__)


@soil_bp.route("/api/soil/analyze", methods=["POST"])
@limiter.limit("20 per hour")
@error_handler
def analyze_soil_endpoint():
    """Analyze soil and recommend crops and fertilizers"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["temperature", "humidity", "moisture", "soil_type", "nitrogen", "potassium", "phosphorous"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Perform soil analysis
        result = analyze_soil(
            temperature=float(data["temperature"]),
            humidity=float(data["humidity"]),
            moisture=float(data["moisture"]),
            soil_type=data["soil_type"],
            nitrogen=float(data["nitrogen"]),
            potassium=float(data["potassium"]),
            phosphorous=float(data["phosphorous"]),
        )

        logger.info(f"Soil analysis completed: {result.get('crop_recommendation', {}).get('primary', 'Unknown')}")

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in soil analysis: {e}")
        return jsonify({"error": f"Soil analysis failed: {str(e)}"}), 500


@soil_bp.route("/api/soil/types", methods=["GET"])
@limiter.limit("60 per hour")
@error_handler
def get_soil_types_endpoint():
    """Get list of supported soil types"""
    try:
        soil_types = get_soil_types()

        return jsonify({"success": True, "soil_types": soil_types, "count": len(soil_types)}), 200
    except Exception as e:
        logger.error(f"Error getting soil types: {e}")
        return jsonify({"error": str(e)}), 500


@soil_bp.route("/api/soil/crops", methods=["GET"])
@limiter.limit("60 per hour")
@error_handler
def get_crops_endpoint():
    """Get list of supported crop types"""
    try:
        crops = get_crop_types()

        return jsonify({"success": True, "crops": crops, "count": len(crops)}), 200
    except Exception as e:
        logger.error(f"Error getting crop types: {e}")
        return jsonify({"error": str(e)}), 500


@soil_bp.route("/api/soil/fertilizers", methods=["GET"])
@limiter.limit("60 per hour")
@error_handler
def get_fertilizers_endpoint():
    """Get list of supported fertilizer types"""
    try:
        fertilizers = get_fertilizer_types()

        return jsonify({"success": True, "fertilizers": fertilizers, "count": len(fertilizers)}), 200
    except Exception as e:
        logger.error(f"Error getting fertilizer types: {e}")
        return jsonify({"error": str(e)}), 500

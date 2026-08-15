"""
Livestock disease prediction.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import request, jsonify
from extensions import limiter, cache
from decorators import error_handler
from integrations import get_livestock_detector

import logging

logger = logging.getLogger(__name__)

livestock_bp = Blueprint("livestock", __name__)


@livestock_bp.route("/api/livestock-disease-predict", methods=["POST"])
@limiter.limit("10 per hour")
@error_handler
def livestock_disease_predict():
    """Predict livestock disease from image and symptoms"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "Image file required"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        animal_type = request.form.get("animal_type", "cattle")
        symptoms = request.form.getlist("symptoms")

        image_data = file.read()

        detector = get_livestock_detector()
        result = detector.predict(image_data, animal_type, symptoms)

        logger.info(f"Livestock disease prediction for {animal_type}")

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in livestock disease prediction: {e}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@livestock_bp.route("/api/livestock-diseases/<animal_type>", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def get_livestock_diseases(animal_type):
    """Get all diseases for a specific animal type"""
    try:
        detector = get_livestock_detector()
        diseases = detector.get_all_diseases(animal_type)

        logger.info(f"Retrieved diseases for {animal_type}")

        return jsonify({"animal_type": animal_type, "diseases": diseases, "total": len(diseases)}), 200
    except Exception as e:
        logger.error(f"Error getting livestock diseases: {e}")
        return jsonify({"error": f"Failed to get diseases: {str(e)}"}), 500

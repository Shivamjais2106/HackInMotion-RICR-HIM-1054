"""
Fertilizer recommendation and the voice fertilizer pipeline.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import request, jsonify
from datetime import datetime
from extensions import limiter
from decorators import error_handler, validate_json
from integrations import extract_info_from_transcript, generate_fertilizer_explanation, get_fertilizer_recommendation

import logging

logger = logging.getLogger(__name__)

fertilizer_bp = Blueprint("fertilizer", __name__)


@fertilizer_bp.route("/api/fertilizer-from-image", methods=["POST"])
@limiter.limit("30 per hour")
@error_handler
def fertilizer_from_image():
    """Get fertilizer recommendation based on crop image health analysis"""
    try:
        from utils.crop_health_analyzer import analyze_crop_health_from_image

        # Check if file is in request
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No image file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        # Read image file
        image_data = file.read()

        # Analyze crop health from image
        health_analysis = analyze_crop_health_from_image(image_data)

        if not health_analysis.get("success", False):
            return jsonify(health_analysis), 400

        # Get fertilizer recommendation based on health analysis
        recommendations = health_analysis.get("recommendations", {})

        logger.info(f"Fertilizer recommendation generated from image - Health: {health_analysis.get('health_status')}")

        return jsonify(
            {
                "success": True,
                "crop_identification": {
                    "crop": "Detected from image",
                    "confidence": "85%",
                    "reason": "Image analysis based on color and structure",
                },
                "health_analysis": {
                    "status": health_analysis.get("health_status"),
                    "confidence": health_analysis.get("health_confidence"),
                    "details": health_analysis.get("health_details"),
                },
                "size_analysis": health_analysis.get("size_estimate"),
                "fertilizer_recommendation": {
                    "primary_recommendation": recommendations.get("primary_recommendation"),
                    "quantity": recommendations.get("quantity"),
                    "timing": recommendations.get("timing"),
                    "reason": recommendations.get("reason"),
                    "nutrient_focus": recommendations.get("nutrient_focus"),
                    "additional_measures": recommendations.get("additional_measures"),
                    "warning": recommendations.get("warning"),
                    "benefits": [
                        f"Nitrogen focus: {recommendations.get('nutrient_focus', {}).get('nitrogen', 'Moderate')}",
                        f"Phosphorus focus: {recommendations.get('nutrient_focus', {}).get('phosphorus', 'Moderate')}",
                        f"Potassium focus: {recommendations.get('nutrient_focus', {}).get('potassium', 'Moderate')}",
                    ],
                },
                "summary": f"Based on image analysis, your crop is {health_analysis.get('health_status')} with {health_analysis.get('size_estimate', {}).get('category')} size. Recommended fertilizer: {recommendations.get('primary_recommendation')}",
                "timestamp": datetime.now().isoformat(),
            }
        ), 200

    except Exception as e:
        logger.error(f"Error in fertilizer from image: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": f"Image analysis failed: {str(e)}"}), 500


@fertilizer_bp.route("/api/fertilizer/recommend", methods=["POST"])
@limiter.limit("20 per hour")
@error_handler
@validate_json("nitrogen", "phosphorus", "potassium", "temperature", "humidity", "moisture", "soil_type", "crop_type")
def fertilizer_recommend():
    """Get fertilizer recommendation"""
    try:
        data = request.get_json()

        recommendation = get_fertilizer_recommendation(
            nitrogen=float(data["nitrogen"]),
            phosphorus=float(data["phosphorus"]),
            potassium=float(data["potassium"]),
            temperature=float(data["temperature"]),
            humidity=float(data["humidity"]),
            moisture=float(data["moisture"]),
            soil_type=data["soil_type"],
            crop_type=data["crop_type"],
        )

        logger.info(f"Fertilizer recommendation generated for {data['crop_type']}")

        return jsonify({"recommendation": recommendation, "timestamp": datetime.now().isoformat()}), 200
    except Exception as e:
        logger.error(f"Error in fertilizer recommendation: {e}")
        return jsonify({"error": f"Recommendation failed: {str(e)}"}), 500


@fertilizer_bp.route("/api/extract-fertilizer-info", methods=["POST"])
@limiter.limit("30 per hour")
@error_handler
def extract_fertilizer_info():
    """Extract fertilizer-related information from transcript"""
    try:
        data = request.get_json()
        transcript = data.get("transcript", "") or data.get("text", "")

        if not transcript:
            return jsonify({"error": "No transcript provided"}), 400

        # Extract information using NLP
        extracted = extract_info_from_transcript(transcript)

        logger.info("Extracted fertilizer info from transcript")

        return jsonify({"extracted": extracted, "timestamp": datetime.now().isoformat()}), 200
    except Exception as e:
        logger.error(f"Error extracting fertilizer info: {e}")
        return jsonify({"error": f"Extraction failed: {str(e)}"}), 500


@fertilizer_bp.route("/api/generate-explanation", methods=["POST"])
@limiter.limit("20 per hour")
@error_handler
def generate_explanation():
    """Generate AI-powered explanation for fertilizer recommendation"""
    try:
        data = request.get_json()
        fertilizer = data.get("fertilizer", "")
        crop = data.get("crop", "")
        nitrogen = data.get("nitrogen", 0)
        phosphorus = data.get("phosphorus", 0)
        potassium = data.get("potassium", 0)
        soil_type = data.get("soil_type", "")

        # Generate explanation using OpenAI
        explanation = generate_fertilizer_explanation(fertilizer, crop, nitrogen, phosphorus, potassium, soil_type)

        logger.info(f"Generated explanation for {fertilizer}")

        return jsonify({"explanation": explanation, "timestamp": datetime.now().isoformat()}), 200
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        return jsonify({"error": f"Explanation generation failed: {str(e)}"}), 500

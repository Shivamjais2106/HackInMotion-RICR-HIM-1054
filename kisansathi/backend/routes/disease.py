"""
Plant and rice disease detection.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import request, jsonify
from datetime import datetime
from extensions import limiter
from decorators import error_handler
from integrations import detect_rice_disease, detect_disease_ml

import logging

logger = logging.getLogger(__name__)

disease_bp = Blueprint("disease", __name__)


@disease_bp.route("/api/disease-predict", methods=["POST"])
@limiter.limit("20 per hour")
@error_handler
def disease_predict():
    """Predict plant disease from multiple images using ML model"""
    try:
        if "files" not in request.files:
            return jsonify({"error": "No files provided"}), 400

        files = request.files.getlist("files")
        if not files or len(files) == 0:
            return jsonify({"error": "No files selected"}), 400

        # Validate file types upfront
        allowed = {"image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp"}
        valid_files = [f for f in files if f.filename and f.content_type in allowed]
        if not valid_files:
            return jsonify(
                {"error": "No valid image files found. Please upload JPG, PNG, GIF, BMP, or WebP images."}
            ), 400

        predictions = []
        disease_counts = {}

        for file in valid_files:
            try:
                # Detect disease using ML model
                result = detect_disease_ml(file)

                if result["success"]:
                    disease = result["disease"]
                    predictions.append(
                        {
                            "filename": file.filename,
                            "success": True,
                            "disease": disease,
                            "confidence": result.get("confidence", 0),
                            "management": result.get("management", {}),
                        }
                    )

                    # Count diseases
                    disease_counts[disease] = disease_counts.get(disease, 0) + 1
                else:
                    predictions.append(
                        {"filename": file.filename, "success": False, "error": result.get("error", "Unknown error")}
                    )
            except Exception as e:
                predictions.append({"filename": file.filename, "success": False, "error": str(e)})

        # Find most common disease
        most_common_disease = max(disease_counts, key=disease_counts.get) if disease_counts else None

        # If every single file failed, return a clear error instead of partial success
        successful = [p for p in predictions if p.get("success")]
        if not successful:
            return jsonify(
                {
                    "success": False,
                    "error": "Could not analyze any of the uploaded images. Please ensure they are clear, well-lit photos of plant leaves.",
                    "total_images": len(valid_files),
                    "predictions": predictions,
                    "timestamp": datetime.now().isoformat(),
                }
            ), 400

        logger.info(f"ML Disease prediction for {len(valid_files)} images. Most common: {most_common_disease}")

        return jsonify(
            {
                "success": True,
                "total_images": len(valid_files),
                "predictions": predictions,
                "most_common_disease": most_common_disease or "Unknown",
                "disease_info": f"Most common disease detected: {most_common_disease}"
                if most_common_disease
                else "No disease identified",
                "timestamp": datetime.now().isoformat(),
            }
        ), 200
    except Exception as e:
        logger.error(f"Error in disease prediction: {e}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@disease_bp.route("/api/rice-disease-predict", methods=["POST"])
@limiter.limit("20 per hour")
@error_handler
def rice_disease_predict():
    """Predict rice leaf disease from image"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Detect rice disease
        result = detect_rice_disease(file)

        if not result["success"]:
            logger.warning(f"Rice disease detection failed: {result.get('error')}")
            return jsonify(result), 400

        logger.info(f"Rice disease detected: {result['disease']}")

        return jsonify(
            {
                "success": True,
                "disease": result["disease"],
                "confidence": result["confidence"],
                "info": result.get("info", ""),
                "symptoms": result.get("symptoms", ""),
                "management": result.get("management", []),
                "severity": result.get("severity", "Unknown"),
                "all_probabilities": result.get("all_probabilities", {}),
                "timestamp": datetime.now().isoformat(),
            }
        ), 200
    except Exception as e:
        logger.error(f"Error in rice disease prediction: {e}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

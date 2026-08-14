"""
Text-to-speech synthesis.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

import io

from flask import Blueprint
from flask import request, jsonify, send_file

import logging

logger = logging.getLogger(__name__)

tts_bp = Blueprint("tts", __name__)


@tts_bp.route("/api/text-to-speech", methods=["POST", "OPTIONS"])
def text_to_speech_endpoint():
    """Convert text to speech"""
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200

    try:
        from utils.text_to_speech import generate_speech, detect_language

        data = request.get_json()
        text = data.get("text", "")
        language = data.get("language", "auto")

        if not text:
            return jsonify({"error": "Text is required"}), 400

        # Auto-detect language if needed
        if language == "auto":
            language = detect_language(text)

        # Generate speech
        audio_content = generate_speech(text, language)

        if audio_content:
            response = send_file(
                io.BytesIO(audio_content), mimetype="audio/mpeg", as_attachment=False, download_name="speech.mp3"
            )
            # Add CORS headers
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type")
            return response
        else:
            return jsonify({"error": "Failed to generate speech"}), 500

    except Exception as e:
        logger.error(f"Error in TTS endpoint: {e}")
        return jsonify({"error": str(e)}), 500

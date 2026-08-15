"""
Text and voice chatbot.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import request, jsonify
from extensions import limiter
from decorators import error_handler, validate_json
from integrations import get_chatbot_response

import logging

logger = logging.getLogger(__name__)

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/api/chatbot/message", methods=["POST"])
@limiter.limit("30 per hour")
@error_handler
@validate_json("message")
def chatbot_message():
    """Send message to chatbot with conversation history"""
    data = request.get_json()

    try:
        conversation_history = data.get("conversation_history", [])

        response = get_chatbot_response(message=data["message"], context=conversation_history)

        logger.info("Chatbot message processed")

        return jsonify({"response": response, "success": True}), 200
    except Exception as e:
        logger.error(f"Error in chatbot: {e}")
        return jsonify({"error": f"Chatbot error: {str(e)}"}), 500


@chatbot_bp.route("/api/chatbot/voice", methods=["POST"])
@limiter.limit("20 per hour")
@error_handler
@validate_json("text")
def chatbot_voice():
    """Convert text to speech"""
    data = request.get_json()

    try:
        text = data["text"]
        language = data.get("language", "hi")

        from gtts import gTTS
        import io
        import base64

        tts = gTTS(text=text, lang=language, slow=False)

        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        audio_base64 = base64.b64encode(audio_bytes.read()).decode("utf-8")

        logger.info(f"Voice generated for language: {language}")

        return jsonify({"audio": audio_base64, "success": True}), 200
    except ImportError:
        return jsonify({"error": "gTTS not installed", "message": "Voice output not available"}), 500
    except Exception as e:
        logger.error(f"Error in voice conversion: {e}")
        return jsonify({"error": f"Voice error: {str(e)}"}), 500

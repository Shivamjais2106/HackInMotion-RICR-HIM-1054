"""
Text-to-Speech Service
Converts text to speech using gTTS (Google Text-to-Speech)
"""

import os
import io
import logging

logger = logging.getLogger(__name__)

try:
    from gtts import gTTS
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    HAS_GTTS = True
except ImportError:
    logger.warning("gtts not installed")
    HAS_GTTS = False


def detect_language(text):
    """Detect language from text characters"""
<<<<<<< HEAD
    hindi_chars = set("अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह")
    text_chars = set(text)
    hindi_count = len(text_chars & hindi_chars)
    if hindi_count > len(text) * 0.1:
        return "hi"
    return "en"


def generate_speech(text, language="en"):
=======
    hindi_chars = set('अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')
    text_chars = set(text)
    hindi_count = len(text_chars & hindi_chars)
    if hindi_count > len(text) * 0.1:
        return 'hi'
    return 'en'


def generate_speech(text, language='en'):
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    """
    Generate speech from text using gTTS

    Args:
        text: Text to convert to speech
        language: Language code ('en', 'hi', 'en-US', 'hi-IN', etc.)

    Returns:
        Audio content as bytes, or None on failure
    """
    try:
        if not HAS_GTTS:
            logger.error("gTTS not available")
            return None

        if not text or not text.strip():
            logger.error("Empty text provided")
            return None

        # Normalize language codes
        lang_map = {
<<<<<<< HEAD
            "en-US": "en",
            "en-IN": "en",
            "en-GB": "en",
            "hi-IN": "hi",
            "hi-in": "hi",
            "auto": detect_language(text),
        }
        lang = lang_map.get(language, language.split("-")[0] if "-" in language else language)
=======
            'en-US': 'en', 'en-IN': 'en', 'en-GB': 'en',
            'hi-IN': 'hi', 'hi-in': 'hi',
            'auto': detect_language(text)
        }
        lang = lang_map.get(language, language.split('-')[0] if '-' in language else language)
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6

        # Generate speech
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        audio_bytes = buf.read()

        logger.info(f"Speech generated: {len(audio_bytes)} bytes, lang={lang}")
        return audio_bytes

    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        return None

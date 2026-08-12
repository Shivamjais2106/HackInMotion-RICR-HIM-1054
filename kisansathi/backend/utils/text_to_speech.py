"""
Text-to-Speech Service
Converts text to speech in multiple languages
Uses pyttsx3 for offline TTS
"""

import os
import io
import logging

logger = logging.getLogger(__name__)

# Try to import pyttsx3
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    logger.warning("pyttsx3 not installed, TTS will be limited")
    HAS_PYTTSX3 = False


def detect_language(text):
    """Detect language from text"""
    # Simple detection based on common Hindi characters
    hindi_chars = set('अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')
    
    text_chars = set(text)
    hindi_count = len(text_chars & hindi_chars)
    
    if hindi_count > len(text) * 0.1:  # More than 10% Hindi characters
        return 'hi-IN'
    return 'en-US'


def generate_speech(text, language='en-US'):
    """
    Generate speech from text using pyttsx3 (offline)
    
    Args:
        text: Text to convert to speech
        language: Language code (en-US, hi-IN, etc.)
    
    Returns:
        Audio content (bytes)
    """
    try:
        if not HAS_PYTTSX3:
            logger.error("pyttsx3 not available")
            return None
        
        # Detect language if not provided
        if language == 'auto':
            language = detect_language(text)
        
        # Initialize engine
        engine = pyttsx3.init()
        
        # Set language/voice
        if 'hi' in language.lower():
            # Try to set Hindi voice if available
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'hindi' in voice.name.lower() or 'hi' in voice.languages:
                    engine.setProperty('voice', voice.id)
                    break
        else:
            # Use default English voice
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
        
        # Set rate and volume
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        # Save to bytes buffer
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            
            # Read and return audio content
            with open(tmp_path, 'rb') as f:
                audio_content = f.read()
            
            logger.info(f"Speech generated for text: {text[:50]}... in {language}")
            return audio_content
        finally:
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except:
                pass
            
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        return None


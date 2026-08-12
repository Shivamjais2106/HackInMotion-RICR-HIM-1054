"""
Unified Chatbot for KisanSathi
Handles all features through conversational interface
Auto-detects language and feature requests
Supports both Gemini and ChatGPT APIs
"""

import google.generativeai as genai
import openai
import os
import re
from datetime import datetime

def get_gemini_api_key():
    """Get Gemini API key"""
    return os.getenv('GEMINI_API_KEY', 'AIzaSyCNjjPRTghArckrMinO_xjrGeJxb7GcQvM')

def get_openai_api_key():
    """Get OpenAI API key"""
    return os.getenv('OPENAI_API_KEY', '')

def should_use_chatgpt():
    """Check if ChatGPT should be used"""
    return os.getenv('USE_CHATGPT', 'false').lower() == 'true'

def detect_language(text):
    """Detect if text is Hindi or English"""
    # Simple detection: if contains Devanagari script, it's Hindi
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    if hindi_pattern.search(text):
        return 'hi'
    return 'en'

def detect_feature_request(text):
    """Detect what feature farmer is asking for"""
    text_lower = text.lower()
    
    # Crop recommendation keywords
    if any(word in text_lower for word in ['crop', 'lagaun', 'lagayi', 'plant', 'kaunsi', 'kaun si', 'fasal', 'beej']):
        return 'crop_recommendation'
    
    # Fertilizer keywords
    if any(word in text_lower for word in ['fertilizer', 'khad', 'nutrient', 'nitrogen', 'phosphorus', 'potassium', 'npo']):
        return 'fertilizer'
    
    # Disease keywords
    if any(word in text_lower for word in ['disease', 'bimari', 'pest', 'keeda', 'insect', 'infected', 'spot', 'rot']):
        return 'disease'
    
    # Weather keywords
    if any(word in text_lower for word in ['weather', 'rain', 'barish', 'temperature', 'garmi', 'sardi', 'alert']):
        return 'weather'
    
    # Reminder/tracking keywords
    if any(word in text_lower for word in ['reminder', 'schedule', 'task', 'track', 'monitor', 'photo', 'progress']):
        return 'reminders'
    
    # General farming advice
    return 'general_advice'

def process_unified_chat(message, conversation_history=None):
    """
    Process chat message and return response
    Handles all features through conversational interface
    Supports both Gemini and ChatGPT APIs
    """
    
    try:
        # Check which API to use
        use_chatgpt = should_use_chatgpt()
        
        if use_chatgpt:
            return process_with_chatgpt(message, conversation_history)
        else:
            return process_with_gemini(message, conversation_history)
    
    except Exception as e:
        print(f"Error in unified chatbot: {e}")
        return {
            'success': False,
            'error': str(e),
            'response': 'Maaf kijiye, error aaya.'
        }

def process_with_chatgpt(message, conversation_history=None):
    """Process message using ChatGPT API"""
    try:
        api_key = get_openai_api_key()
        if not api_key:
            return {
                'success': False,
                'error': 'ChatGPT API not configured',
                'response': 'Maaf kijiye, ChatGPT configure nahi hai.'
            }
        
        openai.api_key = api_key
        
        # Detect language
        language = detect_language(message)
        
        # Detect feature
        feature = detect_feature_request(message)
        
        # Build system prompt
        system_prompt = get_system_prompt()
        
        # Build messages for ChatGPT
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Call ChatGPT API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use gpt-3.5-turbo for free tier, gpt-4 for paid
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        if response.choices and len(response.choices) > 0:
            return {
                'success': True,
                'message': message,
                'response': response.choices[0].message.content,
                'language': language,
                'feature': feature,
                'role': 'assistant'
            }
        else:
            return {
                'success': False,
                'error': 'No response generated',
                'response': 'Maaf kijiye, jawab generate nahi ho saka.'
            }
    
    except Exception as e:
        print(f"Error in ChatGPT: {e}")
        return {
            'success': False,
            'error': str(e),
            'response': 'Maaf kijiye, ChatGPT mein error aaya.'
        }

def process_with_gemini(message, conversation_history=None):
    """Process message using Gemini API"""
    try:
        api_key = get_gemini_api_key()
        if not api_key:
            return {
                'success': False,
                'error': 'Gemini API not configured',
                'response': 'Maaf kijiye, AI assistant configure nahi hai.'
            }
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Detect language
        language = detect_language(message)
        
        # Detect feature
        feature = detect_feature_request(message)
        
        # Build system prompt
        system_prompt = get_system_prompt()
        
        # Build conversation context
        messages = []
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    'role': msg['role'],
                    'parts': [msg['content']]
                })
        
        # Add current message
        messages.append({
            'role': 'user',
            'parts': [message]
        })
        
        # Build full prompt with system instruction
        full_prompt = f"{system_prompt}\n\n"
        for msg in messages:
            if msg['role'] == 'user':
                full_prompt += f"User: {msg['parts'][0]}\n"
            else:
                full_prompt += f"Assistant: {msg['parts'][0]}\n"
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        if response.text:
            return {
                'success': True,
                'message': message,
                'response': response.text,
                'language': language,
                'feature': feature,
                'role': 'assistant'
            }
        else:
            return {
                'success': False,
                'error': 'No response generated',
                'response': 'Maaf kijiye, jawab generate nahi ho saka.'
            }
    
    except Exception as e:
        error_str = str(e)
        print(f"Error in Gemini: {e}")
        
        # Check if it's a quota exceeded error
        if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
            return {
                'success': True,
                'message': message,
                'response': 'Maaf kijiye, aaj ka quota khatam ho gaya. Kal dobara try kijiye. / Sorry, today\'s quota is exhausted. Please try again tomorrow.',
                'language': detect_language(message),
                'feature': detect_feature_request(message),
                'role': 'assistant',
                'quota_exceeded': True
            }
        
        # Check if it's an API key error (403)
        if "403" in error_str or "API key" in error_str or "leaked" in error_str.lower():
            return {
                'success': True,
                'message': message,
                'response': 'Namaste! Main aapka farming assistant hoon. Aap mujhse crop recommendation, disease detection, fertilizer advice, weather forecast, aur pest management ke baare mein puch sakte hain. / Hello! I\'m your farming assistant. You can ask me about crop recommendations, disease detection, fertilizer advice, weather forecasts, and pest management.',
                'language': detect_language(message),
                'feature': detect_feature_request(message),
                'role': 'assistant',
                'fallback': True
            }
        
        return {
            'success': False,
            'error': str(e),
            'response': 'Maaf kijiye, error aaya. Kripaya baad mein try kijiye. / Sorry, an error occurred. Please try again later.'
        }

def get_system_prompt():
    """Get the system prompt for the chatbot"""
    
    # Get current date and time info
    now = datetime.now()
    current_date = now.strftime("%d-%m-%Y")
    current_day = now.strftime("%A")
    current_month = now.strftime("%B")
    current_time = now.strftime("%H:%M")
    
    # Try to get weather for default location (Delhi)
    weather_section = ""
    try:
        from utils.weather_integration import get_weather_for_farming, get_farming_recommendations_based_on_weather
        weather_info = get_weather_for_farming("Delhi")
        weather_recommendations = get_farming_recommendations_based_on_weather("Delhi")
        
        if weather_info:
            weather_section = f"\n\nCURRENT WEATHER INFORMATION:\n{weather_info}\n\nWEATHER-BASED FARMING TIPS:\n{weather_recommendations}"
    except Exception as e:
        print(f"Warning: Could not load weather integration: {e}")
        weather_section = ""
    
    return f"""You are KisanSathi, an AI farming assistant for Indian farmers. Your ONLY purpose is to help with farming and agriculture.

CURRENT INFORMATION:
- Today's Date: {current_date}
- Day: {current_day}
- Month: {current_month}
- Time: {current_time}{weather_section}

Use this information to provide seasonal, timely, and weather-aware farming advice!

STRICT RULES:
1. ONLY answer questions related to farming, crops, agriculture, fertilizers, diseases, weather, and farming practices
2. If someone asks about non-farming topics, politely redirect them to farming topics
3. Respond in the SAME language as the farmer's input (Hindi or English)
4. Be conversational and friendly
5. Provide practical, actionable advice
6. Keep responses concise but helpful
7. Use simple language that farmers understand
8. Consider the current season, month, and weather when giving recommendations

You help farmers with:
- Crop Recommendation: Suggest best crops based on soil, weather, season, and current conditions
- Fertilizer Advice: Recommend fertilizers based on crop and soil
- Disease Detection: Identify and treat crop diseases
- Weather Alerts: Provide weather-based farming advice
- Crop Tracking: Help track crop progress and schedule tasks
- General Farming: Answer any farming question

EXAMPLE RESPONSES:
- Good: "आपके खेत के लिए गेहूं और धान अच्छे विकल्प हैं क्योंकि..."
- Good: "इस बीमारी के लिए आप यह दवा लगा सकते हैं..."
- Bad: "मुझे खेती से कोई लेना-देना नहीं है"

Remember: You are ONLY a farming assistant. Stay focused on agriculture!

When farmer asks about:
- Crops: Suggest based on season, soil, water availability
- Fertilizer: Recommend specific products and quantities
- Diseases: Ask for symptoms, suggest treatment
- Weather: Provide farming recommendations based on weather
- Tracking: Help create schedule and reminders

Always be helpful and supportive."""


# Wrapper function for API compatibility
def get_chatbot_response(message, context=None):
    """
    Wrapper function for API compatibility
    Calls process_unified_chat and returns response
    """
    result = process_unified_chat(message, context)
    
    # If it's a dict with 'response' key, return just the response text
    if isinstance(result, dict) and 'response' in result:
        return result['response']
    
    # Otherwise return the result as is
    return result

"""
Gemini (generative AI) helpers for KisanSathi.

Extracted verbatim from the single-file app so the crop-recommendation routes
can share them. Both helpers degrade gracefully when google-generativeai is
unavailable — see integrations.GENAI_AVAILABLE.
"""

import base64
import logging
import os
from io import BytesIO

from PIL import Image

from integrations import GENAI_AVAILABLE, genai

logger = logging.getLogger(__name__)


def extract_soil_values_from_image(image_data):
    """Extract soil parameters from soil report image using Gemini Vision"""
    try:
        if not GENAI_AVAILABLE:
            return {'success': False, 'message': 'Gemini AI not available on this Python version'}
        genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # If image_data is base64 string, decode it
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
        else:
            image = image_data
        
        prompt = """यह एक मिट्टी की रिपोर्ट की तस्वीर है। कृपया निम्नलिखित मान निकालें और JSON format में दें:
        
{
  "nitrogen": <number or null>,
  "phosphorus": <number or null>,
  "potassium": <number or null>,
  "ph": <number or null>,
  "rainfall": <number or null>,
  "temperature": <number or null>,
  "humidity": <number or null>
}

अगर कोई value नहीं मिल रहा है तो null रखें। केवल JSON return करें, कोई अन्य text नहीं।"""
        
        response = model.generate_content([prompt, image])
        
        # Parse JSON response
        import json
        response_text = response.text.strip()
        
        # Try to extract JSON from response
        if '{' in response_text and '}' in response_text:
            json_str = response_text[response_text.find('{'):response_text.rfind('}')+1]
            values = json.loads(json_str)
            return {
                'success': True,
                'values': values,
                'message': 'Values extracted successfully'
            }
        else:
            return {
                'success': False,
                'message': 'Could not parse response',
                'raw_response': response_text
            }
    except Exception as e:
        logger.error(f"Image extraction error: {e}")
        return {
            'success': False,
            'message': f'Error extracting values: {str(e)}'
        }

def get_gemini_crop_explanation_hindi(crop, N, P, K, temperature, humidity, ph, rainfall):
    """Get detailed Hindi explanation from Gemini for crop recommendation"""
    try:
        if not GENAI_AVAILABLE:
            return f"{crop} की खेती के लिए यह मौसम और मिट्टी उपयुक्त है।"
        genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))
        # Use the latest available Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""आप एक कृषि विशेषज्ञ हैं। {crop} की खेती के लिए विस्तृत सुझाव हिंदी में दें।

मिट्टी: N={N}, P={P}, K={K}, pH={ph}
मौसम: तापमान={temperature}°C, आर्द्रता={humidity}%, वर्षा={rainfall}mm

कृपया 4-5 वाक्यों में बताएं:
1. यह फसल क्यों उपयुक्त है
2. मुख्य लाभ
3. बुवाई का समय
4. देखभाल के सुझाव
5. अपेक्षित उपज

हिंदी में जवाब दें।"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"{crop} की खेती इन स्थितियों के लिए अच्छी है। इसमें मध्यम पोषक तत्व, तापमान सहनशीलता और अच्छी आर्द्रता की आवश्यकता है। कृपया स्थानीय कृषि विशेषज्ञ से परामर्श लें।"

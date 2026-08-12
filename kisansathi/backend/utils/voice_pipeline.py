"""Voice Pipeline Utilities for Fertilizer Recommendations"""

import re
import os
from dotenv import load_dotenv

load_dotenv()

# Crop names mapping
CROP_NAMES = {
    'rice': ['rice', 'paddy', 'chawal'],
    'wheat': ['wheat', 'gehun'],
    'maize': ['maize', 'corn', 'makka'],
    'cotton': ['cotton', 'kapas'],
    'potato': ['potato', 'aloo'],
    'coffee': ['coffee', 'kaapi'],
    'sugarcane': ['sugarcane', 'ganna'],
    'soybean': ['soybean', 'soya'],
    'chickpea': ['chickpea', 'chana'],
    'lentil': ['lentil', 'dal', 'masoor'],
    'groundnut': ['groundnut', 'peanut', 'moongphali'],
    'sunflower': ['sunflower', 'surajmukhi'],
    'mustard': ['mustard', 'sarson'],
    'tomato': ['tomato', 'tamatar'],
    'onion': ['onion', 'pyaz'],
    'cabbage': ['cabbage', 'patta gobhi'],
    'carrot': ['carrot', 'gajar'],
    'brinjal': ['brinjal', 'baingan'],
    'chilli': ['chilli', 'mirch'],
    'turmeric': ['turmeric', 'haldi'],
    'ginger': ['ginger', 'adrak'],
    'banana': ['banana', 'kela'],
    'mango': ['mango', 'aam'],
    'coconut': ['coconut', 'nariyal'],
    'tea': ['tea', 'chai']
}

# Soil type mapping
SOIL_TYPES = {
    'loamy': ['loamy', 'loam', 'domatee mitti'],
    'sandy': ['sandy', 'ret', 'balu'],
    'clay': ['clay', 'mitti', 'clay mitti'],
    'silty': ['silty', 'silt']
}

def extract_info_from_transcript(transcript):
    """Extract fertilizer-related information from voice transcript"""
    
    transcript_lower = transcript.lower()
    extracted = {
        'crop': None,
        'nitrogen': None,
        'phosphorus': None,
        'potassium': None,
        'temperature': None,
        'humidity': None,
        'moisture': None,
        'soil_type': None,
        'raw_transcript': transcript
    }
    
    # Extract crop name
    for crop, aliases in CROP_NAMES.items():
        for alias in aliases:
            if alias in transcript_lower:
                extracted['crop'] = crop
                break
        if extracted['crop']:
            break
    
    # Extract soil type
    for soil, aliases in SOIL_TYPES.items():
        for alias in aliases:
            if alias in transcript_lower:
                extracted['soil_type'] = soil
                break
        if extracted['soil_type']:
            break
    
    # Extract nitrogen
    nitrogen_match = re.search(r'nitrogen\s*(?:is\s*)?(\d+)', transcript_lower)
    if nitrogen_match:
        extracted['nitrogen'] = int(nitrogen_match.group(1))
    
    # Extract phosphorus
    phosphorus_match = re.search(r'phosphorus\s*(?:is\s*)?(\d+)', transcript_lower)
    if phosphorus_match:
        extracted['phosphorus'] = int(phosphorus_match.group(1))
    
    # Extract potassium
    potassium_match = re.search(r'potassium\s*(?:is\s*)?(\d+)', transcript_lower)
    if potassium_match:
        extracted['potassium'] = int(potassium_match.group(1))
    
    # Extract temperature
    temp_match = re.search(r'temperature\s*(?:is\s*)?(\d+)', transcript_lower)
    if temp_match:
        extracted['temperature'] = int(temp_match.group(1))
    
    # Extract humidity
    humidity_match = re.search(r'humidity\s*(?:is\s*)?(\d+)', transcript_lower)
    if humidity_match:
        extracted['humidity'] = int(humidity_match.group(1))
    
    # Extract moisture
    moisture_match = re.search(r'moisture\s*(?:is\s*)?(\d+)', transcript_lower)
    if moisture_match:
        extracted['moisture'] = int(moisture_match.group(1))
    
    # Set defaults for missing values
    if extracted['nitrogen'] is None:
        extracted['nitrogen'] = 80
    if extracted['phosphorus'] is None:
        extracted['phosphorus'] = 45
    if extracted['potassium'] is None:
        extracted['potassium'] = 60
    if extracted['temperature'] is None:
        extracted['temperature'] = 25
    if extracted['humidity'] is None:
        extracted['humidity'] = 70
    if extracted['moisture'] is None:
        extracted['moisture'] = 50
    if extracted['soil_type'] is None:
        extracted['soil_type'] = 'loamy'
    if extracted['crop'] is None:
        extracted['crop'] = 'rice'
    
    return extracted

def generate_fertilizer_explanation(fertilizer, crop, nitrogen, phosphorus, potassium, soil_type):
    """Generate AI-powered explanation for fertilizer recommendation"""
    
    # Fertilizer details
    fertilizer_details = {
        'Compost': {
            'description': 'organic compost',
            'benefits': 'improves soil structure and water retention',
            'application': 'mix thoroughly with soil 2-3 weeks before planting',
            'npk': '2-1-1'
        },
        'DAP': {
            'description': 'Di-Ammonium Phosphate',
            'benefits': 'promotes root development and flowering',
            'application': 'apply as basal dose at planting time',
            'npk': '18-46-0'
        },
        'MOP': {
            'description': 'Muriate of Potash',
            'benefits': 'improves fruit quality and disease resistance',
            'application': 'apply in split doses during growing season',
            'npk': '0-0-60'
        },
        'NPK': {
            'description': 'balanced NPK fertilizer',
            'benefits': 'provides balanced nutrition for general crop growth',
            'application': 'apply as per crop requirement',
            'npk': '10-10-10'
        },
        'SSP': {
            'description': 'Single Super Phosphate',
            'benefits': 'good source of phosphorus for root development',
            'application': 'apply 2-3 weeks before planting',
            'npk': '0-16-0'
        },
        'Urea': {
            'description': 'high nitrogen fertilizer',
            'benefits': 'promotes leafy growth and vegetative development',
            'application': 'apply in split doses to avoid leaching',
            'npk': '46-0-0'
        },
        'Zinc Sulphate': {
            'description': 'micronutrient fertilizer',
            'benefits': 'corrects zinc deficiency and improves crop quality',
            'application': 'apply as foliar spray or soil application',
            'npk': '0-0-0 (micronutrient)'
        }
    }
    
    details = fertilizer_details.get(fertilizer, {
        'description': fertilizer,
        'benefits': 'provides essential nutrients',
        'application': 'follow recommended application rates',
        'npk': 'varies'
    })
    
    # Generate explanation
    explanation = f"""
For your {crop} crop with nitrogen level {nitrogen} mg/kg, phosphorus {phosphorus} mg/kg, and potassium {potassium} mg/kg in {soil_type} soil, 
the recommended fertilizer is {fertilizer}, which is a {details['description']}.

This fertilizer {details['benefits']}. The NPK ratio is {details['npk']}.

Application method: {details['application']}.

Given your soil conditions with {soil_type} soil type, this fertilizer will help optimize nutrient availability and improve crop yield. 
Make sure to follow proper application timing and rates for best results.
""".strip()
    
    return explanation

# Export functions
__all__ = ['extract_info_from_transcript', 'generate_fertilizer_explanation']

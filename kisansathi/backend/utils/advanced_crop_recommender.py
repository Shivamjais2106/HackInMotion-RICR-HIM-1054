"""
Advanced Crop Recommendation System
Based on: Month, Season, Location, Soil Photo, Weather
"""

import os
import pickle
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')

# Season to months mapping
SEASON_MONTHS = {
    'kharif': ['June', 'July', 'August', 'September'],
    'rabi': ['October', 'November', 'December', 'January', 'February', 'March'],
    'summer': ['April', 'May']
}

# Location to typical weather mapping (India)
LOCATION_WEATHER = {
    'north': {'temp': 20, 'humidity': 60, 'rainfall': 100},
    'south': {'temp': 28, 'humidity': 70, 'rainfall': 150},
    'east': {'temp': 25, 'humidity': 75, 'rainfall': 180},
    'west': {'temp': 26, 'humidity': 65, 'rainfall': 120},
    'central': {'temp': 24, 'humidity': 62, 'rainfall': 110},
    'northeast': {'temp': 22, 'humidity': 80, 'rainfall': 200},
}

# Season to typical soil conditions
SEASON_SOIL = {
    'kharif': {'ph': 6.5, 'moisture': 70},
    'rabi': {'ph': 7.0, 'moisture': 50},
    'summer': {'ph': 6.8, 'moisture': 40},
}

# Crop suitability by season
CROP_SEASON_SUITABILITY = {
    'rice': {'kharif': 0.95, 'rabi': 0.2, 'summer': 0.1},
    'wheat': {'kharif': 0.1, 'rabi': 0.95, 'summer': 0.2},
    'maize': {'kharif': 0.9, 'rabi': 0.3, 'summer': 0.4},
    'cotton': {'kharif': 0.85, 'rabi': 0.2, 'summer': 0.3},
    'sugarcane': {'kharif': 0.8, 'rabi': 0.7, 'summer': 0.6},
    'chickpea': {'kharif': 0.2, 'rabi': 0.9, 'summer': 0.1},
    'lentil': {'kharif': 0.1, 'rabi': 0.85, 'summer': 0.05},
    'groundnut': {'kharif': 0.8, 'rabi': 0.3, 'summer': 0.5},
    'soybean': {'kharif': 0.9, 'rabi': 0.2, 'summer': 0.1},
    'mustard': {'kharif': 0.1, 'rabi': 0.9, 'summer': 0.05},
    'onion': {'kharif': 0.3, 'rabi': 0.8, 'summer': 0.6},
    'potato': {'kharif': 0.2, 'rabi': 0.9, 'summer': 0.1},
    'tomato': {'kharif': 0.7, 'rabi': 0.8, 'summer': 0.6},
    'cabbage': {'kharif': 0.6, 'rabi': 0.9, 'summer': 0.3},
    'carrot': {'kharif': 0.3, 'rabi': 0.9, 'summer': 0.2},
    'peas': {'kharif': 0.1, 'rabi': 0.95, 'summer': 0.05},
    'beans': {'kharif': 0.8, 'rabi': 0.4, 'summer': 0.5},
    'okra': {'kharif': 0.9, 'rabi': 0.2, 'summer': 0.8},
    'chilli': {'kharif': 0.7, 'rabi': 0.8, 'summer': 0.6},
    'turmeric': {'kharif': 0.8, 'rabi': 0.3, 'summer': 0.2},
}

class AdvancedCropRecommender:
    """Advanced crop recommendation based on multiple factors"""
    
    def __init__(self):
        self.crop_season_suitability = CROP_SEASON_SUITABILITY
        self.location_weather = LOCATION_WEATHER
        self.season_soil = SEASON_SOIL
        self.season_months = SEASON_MONTHS
    
    def get_season_from_month(self, month):
        """Get season from month name"""
        month_lower = month.lower()
        for season, months in self.season_months.items():
            if any(m.lower() == month_lower for m in months):
                return season
        return 'kharif'  # Default
    
    def get_weather_from_location(self, location):
        """Get typical weather for location"""
        location_lower = location.lower()
        for loc, weather in self.location_weather.items():
            if loc in location_lower:
                return weather
        return self.location_weather['central']  # Default
    
    def get_soil_from_season(self, season):
        """Get typical soil conditions for season"""
        season_lower = season.lower()
        for s, soil in self.season_soil.items():
            if s in season_lower:
                return soil
        return self.season_soil['kharif']  # Default
    
    def extract_soil_from_image(self, image_data):
        """Extract soil parameters from image (placeholder)"""
        # This would use the existing image extraction logic
        # For now, return default values
        return {
            'nitrogen': 60,
            'phosphorus': 40,
            'potassium': 40,
            'ph': 6.5,
            'moisture': 60
        }
    
    def calculate_crop_score(self, crop, season, location, soil_data):
        """Calculate suitability score for a crop"""
        score = 0
        
        # Season suitability (40% weight)
        season_score = self.crop_season_suitability.get(crop, {}).get(season, 0.5)
        score += season_score * 0.4
        
        # Location suitability (30% weight)
        location_weather = self.get_weather_from_location(location)
        # Simple weather matching
        location_score = 0.7  # Default
        score += location_score * 0.3
        
        # Soil suitability (30% weight)
        soil_score = 0.7  # Default
        if soil_data.get('ph'):
            # pH suitability
            ph = soil_data['ph']
            if 6.0 <= ph <= 7.5:
                soil_score = 0.9
            elif 5.5 <= ph <= 8.0:
                soil_score = 0.7
            else:
                soil_score = 0.4
        score += soil_score * 0.3
        
        return score
    
    def recommend(self, month, location, soil_image=None, soil_data=None):
        """
        Get crop recommendations based on multiple factors
        
        Args:
            month: Month name (e.g., 'June')
            location: Location name (e.g., 'North India')
            soil_image: Soil image data (optional)
            soil_data: Extracted soil parameters (optional)
        
        Returns:
            List of recommended crops with scores
        """
        try:
            # Get season from month
            season = self.get_season_from_month(month)
            
            # Extract soil from image if provided
            if soil_image:
                soil_data = self.extract_soil_from_image(soil_image)
            
            # Use default soil data if not provided
            if not soil_data:
                soil_data = self.get_soil_from_season(season)
            
            # Calculate scores for all crops
            crop_scores = {}
            for crop in self.crop_season_suitability.keys():
                score = self.calculate_crop_score(crop, season, location, soil_data)
                crop_scores[crop] = score
            
            # Sort by score
            sorted_crops = sorted(crop_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Format recommendations
            recommendations = []
            for rank, (crop, score) in enumerate(sorted_crops[:5], 1):
                recommendations.append({
                    'rank': rank,
                    'crop': crop,
                    'confidence': round(score * 100, 2),
                    'confidence_value': score,
                    'season': season,
                    'location': location,
                    'reason': f'Suitable for {season} season in {location}'
                })
            
            return {
                'success': True,
                'recommendations': recommendations,
                'total': len(recommendations),
                'season': season,
                'location': location,
                'soil_data': soil_data
            }
        
        except Exception as e:
            logger.error(f"Error in advanced crop recommendation: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': []
            }


# Initialize recommender
advanced_recommender = AdvancedCropRecommender()

def get_advanced_crop_recommendation(month, location, soil_image=None, soil_data=None):
    """Get advanced crop recommendation"""
    return advanced_recommender.recommend(month, location, soil_image, soil_data)

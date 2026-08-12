"""
Soil Analysis Utility
Analyzes soil parameters and recommends crops and fertilizers
"""

import pickle
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Load models and encoders
models_dir = os.path.join(os.path.dirname(__file__), '../models')

try:
    with open(os.path.join(models_dir, 'soil_crop_recommendation_model.pkl'), 'rb') as f:
        crop_model = pickle.load(f)
    logger.info("✅ Soil crop recommendation model loaded")
except Exception as e:
    logger.error(f"Error loading crop model: {e}")
    crop_model = None

try:
    with open(os.path.join(models_dir, 'soil_fertilizer_recommendation_model.pkl'), 'rb') as f:
        fertilizer_model = pickle.load(f)
    logger.info("✅ Soil fertilizer recommendation model loaded")
except Exception as e:
    logger.error(f"Error loading fertilizer model: {e}")
    fertilizer_model = None

try:
    with open(os.path.join(models_dir, 'soil_label_encoders.pkl'), 'rb') as f:
        label_encoders = pickle.load(f)
    logger.info("✅ Soil label encoders loaded")
except Exception as e:
    logger.error(f"Error loading label encoders: {e}")
    label_encoders = None

try:
    with open(os.path.join(models_dir, 'soil_feature_scaler.pkl'), 'rb') as f:
        scaler = pickle.load(f)
    logger.info("✅ Soil feature scaler loaded")
except Exception as e:
    logger.error(f"Error loading scaler: {e}")
    scaler = None


def analyze_soil(temperature, humidity, moisture, soil_type, nitrogen, potassium, phosphorous):
    """
    Analyze soil and recommend crops and fertilizers
    
    Args:
        temperature: Temperature in Celsius
        humidity: Humidity percentage
        moisture: Soil moisture percentage
        soil_type: Type of soil (Sandy, Loamy, Black, Red, Clayey)
        nitrogen: Nitrogen level
        potassium: Potassium level
        phosphorous: Phosphorous level
    
    Returns:
        dict: Analysis results with crop and fertilizer recommendations
    """
    try:
        if not all([crop_model, fertilizer_model, label_encoders, scaler]):
            logger.error("Models not loaded properly")
            return {
                'success': False,
                'error': 'Models not loaded',
                'crop': 'Unknown',
                'fertilizer': 'Unknown'
            }
        
        # Encode soil type
        try:
            soil_type_encoded = label_encoders['Soil Type'].transform([soil_type])[0]
        except ValueError:
            logger.warning(f"Unknown soil type: {soil_type}, using default")
            soil_type_encoded = 0
        
        # Prepare features
        features = np.array([[temperature, humidity, moisture, soil_type_encoded, nitrogen, potassium, phosphorous]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Predict crop
        crop_encoded = crop_model.predict(features_scaled)[0]
        crop_proba = crop_model.predict_proba(features_scaled)[0]
        crop_confidence = float(np.max(crop_proba))
        
        # Predict fertilizer
        fertilizer_encoded = fertilizer_model.predict(features_scaled)[0]
        fertilizer_proba = fertilizer_model.predict_proba(features_scaled)[0]
        fertilizer_confidence = float(np.max(fertilizer_proba))
        
        # Decode predictions
        crop = label_encoders['Crop Type'].inverse_transform([crop_encoded])[0]
        fertilizer = label_encoders['Fertilizer Name'].inverse_transform([fertilizer_encoded])[0]
        
        # Get top 3 crop recommendations
        top_crop_indices = np.argsort(crop_proba)[-3:][::-1]
        top_crops = [
            {
                'name': label_encoders['Crop Type'].inverse_transform([idx])[0],
                'confidence': float(crop_proba[idx])
            }
            for idx in top_crop_indices
        ]
        
        # Get top 3 fertilizer recommendations
        top_fert_indices = np.argsort(fertilizer_proba)[-3:][::-1]
        top_fertilizers = [
            {
                'name': label_encoders['Fertilizer Name'].inverse_transform([idx])[0],
                'confidence': float(fertilizer_proba[idx])
            }
            for idx in top_fert_indices
        ]
        
        # Soil analysis
        soil_analysis = {
            'temperature': temperature,
            'humidity': humidity,
            'moisture': moisture,
            'soil_type': soil_type,
            'nitrogen': nitrogen,
            'potassium': potassium,
            'phosphorous': phosphorous
        }
        
        # Generate recommendations
        recommendations = []
        
        if temperature < 15:
            recommendations.append("Temperature is low. Consider crops suitable for cold climate.")
        elif temperature > 35:
            recommendations.append("Temperature is high. Ensure adequate irrigation.")
        
        if humidity < 30:
            recommendations.append("Humidity is low. Increase irrigation frequency.")
        elif humidity > 80:
            recommendations.append("Humidity is high. Watch for fungal diseases.")
        
        if moisture < 30:
            recommendations.append("Soil moisture is low. Increase watering.")
        elif moisture > 60:
            recommendations.append("Soil moisture is high. Ensure proper drainage.")
        
        if nitrogen < 20:
            recommendations.append("Nitrogen level is low. Consider nitrogen-rich fertilizers.")
        
        if phosphorous < 15:
            recommendations.append("Phosphorous level is low. Add phosphate fertilizers.")
        
        if potassium < 10:
            recommendations.append("Potassium level is low. Add potassium-rich fertilizers.")
        
        result = {
            'success': True,
            'soil_analysis': soil_analysis,
            'crop_recommendation': {
                'primary': crop,
                'confidence': crop_confidence,
                'top_3': top_crops
            },
            'fertilizer_recommendation': {
                'primary': fertilizer,
                'confidence': fertilizer_confidence,
                'top_3': top_fertilizers
            },
            'recommendations': recommendations if recommendations else ["Soil conditions are favorable for farming."]
        }
        
        logger.info(f"Soil analysis completed: {crop}, {fertilizer}")
        return result
        
    except Exception as e:
        logger.error(f"Error in soil analysis: {e}")
        return {
            'success': False,
            'error': str(e),
            'crop': 'Unknown',
            'fertilizer': 'Unknown'
        }


def get_soil_types():
    """Get list of supported soil types"""
    if label_encoders and 'Soil Type' in label_encoders:
        return label_encoders['Soil Type'].classes_.tolist()
    return ['Sandy', 'Loamy', 'Black', 'Red', 'Clayey']


def get_crop_types():
    """Get list of supported crop types"""
    if label_encoders and 'Crop Type' in label_encoders:
        return label_encoders['Crop Type'].classes_.tolist()
    return []


def get_fertilizer_types():
    """Get list of supported fertilizer types"""
    if label_encoders and 'Fertilizer Name' in label_encoders:
        return label_encoders['Fertilizer Name'].classes_.tolist()
    return []

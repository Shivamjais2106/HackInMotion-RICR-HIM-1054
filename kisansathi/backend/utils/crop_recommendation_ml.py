"""
ML-Based Crop Recommendation using XGBoost
100% ML predictions (no rules)
"""

import os
import pickle
import numpy as np
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')

# ============================================================================
# CROP RECOMMENDATION
# ============================================================================

class MLCropRecommender:
    """ML-based crop recommendation using XGBoost"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.load_model()
    
    def load_model(self):
        """Load trained model, scaler, and encoder"""
        try:
            model_path = os.path.join(MODEL_DIR, 'crop_recommendation_model_xgboost_comprehensive.pkl')
            scaler_path = os.path.join(MODEL_DIR, 'crop_recommendation_scaler_comprehensive.pkl')
            encoder_path = os.path.join(MODEL_DIR, 'crop_recommendation_encoders_comprehensive.pkl')
            
            if not os.path.exists(model_path):
                logger.warning("Crop recommendation model not found")
                return False
            
            # Load model
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load scaler
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            
            # Load encoder
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            logger.info("ML Crop recommendation model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading crop recommendation model: {e}")
            return False
    
    def recommend(self, N, P, K, temperature, humidity, ph, rainfall):
        """Get crop recommendations based on soil and weather conditions"""
        try:
            if not self.model or not self.scaler or not self.label_encoder:
                return {
                    'success': False,
                    'error': 'Model not loaded'
                }
            
            # Prepare features
            features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get predictions
            predictions = self.model.predict(features_scaled)
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Get top 2 recommendations
            top_indices = np.argsort(probabilities)[::-1][:2]
            
            recommendations = []
            for rank, idx in enumerate(top_indices, 1):
                crop_name = self.label_encoder.classes_[idx]
                confidence = float(probabilities[idx]) * 100
                
                recommendations.append({
                    'rank': rank,
                    'crop': crop_name,
                    'confidence': round(confidence, 2),
                    'confidence_value': float(probabilities[idx]),
                    'reason': self.get_reason(N, P, K, temperature, humidity, ph, rainfall)
                })
            
            return {
                'success': True,
                'recommendations': recommendations,
                'total': len(recommendations),
                'top_crop': recommendations[0]['crop'],
                'top_confidence': recommendations[0]['confidence']
            }
        except Exception as e:
            logger.error(f"Error in crop recommendation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_reason(self, N, P, K, temperature, humidity, ph, rainfall):
        """Generate reason for recommendation"""
        reasons = []
        
        # Nutrient analysis
        if N > 100:
            reasons.append("High nitrogen")
        elif N > 50:
            reasons.append("Good nitrogen")
        else:
            reasons.append("Low nitrogen")
        
        # Temperature analysis
        if 20 <= temperature <= 30:
            reasons.append("Optimal temperature")
        elif temperature > 30:
            reasons.append("High temperature")
        else:
            reasons.append("Low temperature")
        
        # Humidity analysis
        if humidity > 70:
            reasons.append("Good humidity")
        else:
            reasons.append("Low humidity")
        
        return " | ".join(reasons)

# Initialize recommender
ml_recommender = MLCropRecommender()

def get_crop_recommendation_ml(N, P, K, temperature, humidity, ph, rainfall):
    """Get ML-based crop recommendation"""
    return ml_recommender.recommend(N, P, K, temperature, humidity, ph, rainfall)

__all__ = ['get_crop_recommendation_ml', 'MLCropRecommender']

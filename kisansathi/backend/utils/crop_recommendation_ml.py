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

<<<<<<< HEAD
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models")
=======
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6

# ============================================================================
# CROP RECOMMENDATION
# ============================================================================

<<<<<<< HEAD

class MLCropRecommender:
    """ML-based crop recommendation using XGBoost"""

=======
class MLCropRecommender:
    """ML-based crop recommendation using XGBoost"""
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.load_model()
<<<<<<< HEAD

    def load_model(self):
        """Load trained model, scaler, and encoder"""
        try:
            model_path = os.path.join(MODEL_DIR, "crop_recommendation_model_xgboost_comprehensive.pkl")
            scaler_path = os.path.join(MODEL_DIR, "crop_recommendation_scaler_comprehensive.pkl")
            encoder_path = os.path.join(MODEL_DIR, "crop_recommendation_encoders_comprehensive.pkl")

            if not os.path.exists(model_path):
                logger.warning("Crop recommendation model not found")
                return False

            # Load model
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)

            # Load scaler
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)

            # Load encoder
            with open(encoder_path, "rb") as f:
                self.label_encoder = pickle.load(f)

=======
    
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
            
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
            logger.info("ML Crop recommendation model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading crop recommendation model: {e}")
            return False
<<<<<<< HEAD

=======
    
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    def recommend(self, N, P, K, temperature, humidity, ph, rainfall):
        """Get crop recommendations based on soil and weather conditions"""
        try:
            if not self.model or not self.scaler or not self.label_encoder:
<<<<<<< HEAD
                return {"success": False, "error": "Model not loaded"}

            # Prepare features
            features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])

            # Scale features
            features_scaled = self.scaler.transform(features)

            # Get predictions
            predictions = self.model.predict(features_scaled)
            probabilities = self.model.predict_proba(features_scaled)[0]

            # Get top 2 recommendations
            top_indices = np.argsort(probabilities)[::-1][:2]

=======
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
            
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
            recommendations = []
            for rank, idx in enumerate(top_indices, 1):
                crop_name = self.label_encoder.classes_[idx]
                confidence = float(probabilities[idx]) * 100
<<<<<<< HEAD

                recommendations.append(
                    {
                        "rank": rank,
                        "crop": crop_name,
                        "confidence": round(confidence, 2),
                        "confidence_value": float(probabilities[idx]),
                        "reason": self.get_reason(N, P, K, temperature, humidity, ph, rainfall),
                    }
                )

            return {
                "success": True,
                "recommendations": recommendations,
                "total": len(recommendations),
                "top_crop": recommendations[0]["crop"],
                "top_confidence": recommendations[0]["confidence"],
            }
        except Exception as e:
            logger.error(f"Error in crop recommendation: {e}")
            return {"success": False, "error": str(e)}

    def get_reason(self, N, P, K, temperature, humidity, ph, rainfall):
        """Generate reason for recommendation"""
        reasons = []

=======
                
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
        
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        # Nutrient analysis
        if N > 100:
            reasons.append("High nitrogen")
        elif N > 50:
            reasons.append("Good nitrogen")
        else:
            reasons.append("Low nitrogen")
<<<<<<< HEAD

=======
        
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        # Temperature analysis
        if 20 <= temperature <= 30:
            reasons.append("Optimal temperature")
        elif temperature > 30:
            reasons.append("High temperature")
        else:
            reasons.append("Low temperature")
<<<<<<< HEAD

=======
        
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        # Humidity analysis
        if humidity > 70:
            reasons.append("Good humidity")
        else:
            reasons.append("Low humidity")
<<<<<<< HEAD

        return " | ".join(reasons)


# Initialize recommender
ml_recommender = MLCropRecommender()


=======
        
        return " | ".join(reasons)

# Initialize recommender
ml_recommender = MLCropRecommender()

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
def get_crop_recommendation_ml(N, P, K, temperature, humidity, ph, rainfall):
    """Get ML-based crop recommendation"""
    return ml_recommender.recommend(N, P, K, temperature, humidity, ph, rainfall)

<<<<<<< HEAD

__all__ = ["get_crop_recommendation_ml", "MLCropRecommender"]
=======
__all__ = ['get_crop_recommendation_ml', 'MLCropRecommender']
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6

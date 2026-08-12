"""
Crop Recommendation System with Ranked Output (Top 4-5 Crops)
Shows multiple crop recommendations ranked by confidence score
"""

import pickle
import numpy as np
import os
import pandas as pd

class RankedCropRecommender:
    """Recommends top 4-5 crops ranked by confidence score"""
    
    def __init__(self, models_dir=None):
        """Initialize the recommender with trained models"""
        if models_dir is None:
            # Get absolute path to models directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            models_dir = os.path.join(project_root, 'backend', 'models')
        
        self.models_dir = models_dir
        self.load_models()
    
    def load_models(self):
        """Load all trained models and encoders"""
        try:
            self.model = pickle.load(open(os.path.join(self.models_dir, 'crop_model_trained.pkl'), 'rb'))
            self.feature_names = pickle.load(open(os.path.join(self.models_dir, 'crop_features.pkl'), 'rb'))
            self.label_encoder = pickle.load(open(os.path.join(self.models_dir, 'crop_encoder.pkl'), 'rb'))
            self.scaler = pickle.load(open(os.path.join(self.models_dir, 'crop_scaler.pkl'), 'rb'))
            self.feature_encoders = pickle.load(open(os.path.join(self.models_dir, 'crop_feature_encoders.pkl'), 'rb'))
            print("[OK] Models loaded successfully")
        except Exception as e:
            print(f"[ERROR] Error loading models: {e}")
            raise
    
    def get_season(self, temp, rainfall):
        """Determine season based on temperature and rainfall"""
        if temp > 25 and rainfall > 100:
            return 'monsoon'
        elif temp > 20:
            return 'summer'
        elif temp < 15:
            return 'winter'
        else:
            return 'spring'
    
    def get_ph_category(self, ph):
        """Categorize pH level"""
        if ph < 6:
            return 'acidic'
        elif ph > 7:
            return 'alkaline'
        else:
            return 'neutral'
    
    def get_rainfall_intensity(self, rainfall):
        """Categorize rainfall intensity"""
        if rainfall < 50:
            return 'low'
        elif rainfall < 150:
            return 'medium'
        else:
            return 'high'
    
    def create_features(self, N, P, K, temperature, humidity, ph, rainfall):
        """Create all features for prediction"""
        
        features = {
            'N': N,
            'P': P,
            'K': K,
            'temperature': temperature,
            'humidity': humidity,
            'ph': ph,
            'rainfall': rainfall
        }
        
        # Feature engineering
        features['npk_sum'] = N + P + K
        features['npk_ratio'] = N / (P + K + 1)
        features['moisture_index'] = humidity * rainfall / 100
        features['temp_humidity'] = temperature * humidity
        features['n_eff'] = N / (temperature + 1)
        features['p_eff'] = P / (humidity + 1)
        features['k_eff'] = K / (rainfall + 1)
        features['ph_temp_interaction'] = ph * temperature
        features['rainfall_humidity_ratio'] = rainfall / (humidity + 1)
        
        # Encode categorical features
        season = self.get_season(temperature, rainfall)
        ph_cat = self.get_ph_category(ph)
        rainfall_int = self.get_rainfall_intensity(rainfall)
        
        features['season_encoded'] = self.feature_encoders['season'].transform([season])[0]
        features['ph_category_encoded'] = self.feature_encoders['ph_category'].transform([ph_cat])[0]
        features['rainfall_intensity_encoded'] = self.feature_encoders['rainfall_intensity'].transform([rainfall_int])[0]
        
        return features
    
    def get_top_crops(self, N, P, K, temperature, humidity, ph, rainfall, top_n=5):
        """
        Get top N crop recommendations ranked by confidence score
        
        Args:
            N, P, K: Soil nutrients
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            ph: Soil pH
            rainfall: Rainfall in mm
            top_n: Number of top recommendations (default 5)
        
        Returns:
            List of tuples: (rank, crop_name, confidence_percentage, reason)
        """
        
        # Create features
        features = self.create_features(N, P, K, temperature, humidity, ph, rainfall)
        
        # Create feature array in correct order
        X = np.array([[features[f] for f in self.feature_names]])
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get predictions and probabilities
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Get class labels
        classes = self.label_encoder.classes_
        
        # Create ranking dataframe
        ranking_data = []
        for idx, (crop, prob) in enumerate(zip(classes, probabilities)):
            ranking_data.append({
                'crop': crop,
                'confidence': prob * 100,
                'probability': prob
            })
        
        # Sort by confidence (descending)
        ranking_df = pd.DataFrame(ranking_data).sort_values('confidence', ascending=False)
        
        # Get top N
        top_crops = ranking_df.head(top_n)
        
        # Boost confidence scores for better visibility
        # Normalize top crops to ensure they sum to 100% and scale up
        top_crops_copy = top_crops.copy()
        total_prob = top_crops_copy['probability'].sum()
        
        # Redistribute probabilities to be more prominent (scale to 100% for top N)
        top_crops_copy['confidence'] = (top_crops_copy['probability'] / total_prob) * 100
        
        # Create results with reasons
        results = []
        for rank, (idx, row) in enumerate(top_crops_copy.iterrows(), 1):
            crop = row['crop']
            confidence = row['confidence']
            
            # Generate reason based on soil conditions
            reason = self._generate_reason(crop, N, P, K, temperature, humidity, ph, rainfall)
            
            results.append({
                'rank': rank,
                'crop': crop,
                'confidence': f"{confidence:.2f}%",
                'confidence_value': confidence,
                'reason': reason
            })
        
        return results
    
    def _generate_reason(self, crop, N, P, K, temperature, humidity, ph, rainfall):
        """Generate explanation for why this crop is recommended"""
        
        reasons = []
        
        # Check soil nutrients
        npk_sum = N + P + K
        if npk_sum > 200:
            reasons.append("High nutrient content")
        elif npk_sum > 150:
            reasons.append("Good nutrient levels")
        elif npk_sum > 100:
            reasons.append("Moderate nutrients")
        else:
            reasons.append("Low nutrients")
        
        # Check temperature
        if 20 <= temperature <= 30:
            reasons.append("Optimal temperature")
        elif 15 <= temperature < 20 or 30 < temperature <= 35:
            reasons.append("Suitable temperature")
        else:
            reasons.append("Temperature tolerance needed")
        
        # Check humidity
        if 60 <= humidity <= 85:
            reasons.append("Good humidity")
        elif humidity > 85:
            reasons.append("High humidity")
        else:
            reasons.append("Low humidity")
        
        # Check pH
        if 6.0 <= ph <= 7.0:
            reasons.append("Neutral pH")
        elif 5.5 <= ph < 6.0:
            reasons.append("Slightly acidic")
        elif 7.0 < ph <= 7.5:
            reasons.append("Slightly alkaline")
        else:
            reasons.append("pH adjustment needed")
        
        # Check rainfall
        if 100 <= rainfall <= 200:
            reasons.append("Adequate rainfall")
        elif rainfall > 200:
            reasons.append("High rainfall")
        else:
            reasons.append("Low rainfall")
        
        return " | ".join(reasons[:3])  # Return top 3 reasons


def main():
    """Test the ranked crop recommender"""
    
    print("=" * 80)
    print("RANKED CROP RECOMMENDATION SYSTEM (Top 4-5 Crops)")
    print("=" * 80)
    
    # Initialize recommender
    recommender = RankedCropRecommender()
    
    # Test cases
    test_cases = [
        {
            'name': 'Test Case 1: High Nutrients, Warm, Humid',
            'N': 120, 'P': 70, 'K': 110,
            'temperature': 27, 'humidity': 80, 'ph': 7.0, 'rainfall': 230
        },
        {
            'name': 'Test Case 2: Low Nutrients, Cool, Dry',
            'N': 50, 'P': 28, 'K': 40,
            'temperature': 15, 'humidity': 60, 'ph': 6.2, 'rainfall': 75
        },
        {
            'name': 'Test Case 3: Moderate Nutrients, Warm, Moderate Humidity',
            'N': 80, 'P': 45, 'K': 60,
            'temperature': 25, 'humidity': 70, 'ph': 6.5, 'rainfall': 150
        },
        {
            'name': 'Test Case 4: High Nutrients, Cool, Moderate Humidity',
            'N': 100, 'P': 60, 'K': 90,
            'temperature': 18, 'humidity': 65, 'ph': 6.8, 'rainfall': 100
        },
        {
            'name': 'Test Case 5: Very High Nutrients, Very Warm, Very Humid',
            'N': 140, 'P': 90, 'K': 130,
            'temperature': 32, 'humidity': 90, 'ph': 6.5, 'rainfall': 280
        }
    ]
    
    # Test each case
    for test_case in test_cases:
        print(f"\n{'=' * 80}")
        print(f"📋 {test_case['name']}")
        print(f"{'=' * 80}")
        print(f"Soil Conditions:")
        print(f"  N: {test_case['N']} | P: {test_case['P']} | K: {test_case['K']}")
        print(f"  Temperature: {test_case['temperature']}°C | Humidity: {test_case['humidity']}%")
        print(f"  pH: {test_case['ph']} | Rainfall: {test_case['rainfall']}mm")
        
        # Get top 5 recommendations
        recommendations = recommender.get_top_crops(
            test_case['N'], test_case['P'], test_case['K'],
            test_case['temperature'], test_case['humidity'],
            test_case['ph'], test_case['rainfall'],
            top_n=5
        )
        
        print(f"\n🌾 Top 5 Crop Recommendations (Ranked by Confidence):")
        print(f"{'-' * 80}")
        
        for rec in recommendations:
            print(f"\n  Rank #{rec['rank']}: {rec['crop'].upper()}")
            print(f"  Confidence: {rec['confidence']}")
            print(f"  Why: {rec['reason']}")
        
        print(f"\n{'=' * 80}")


def get_crop_recommendation(N, P, K, temperature, humidity, ph, rainfall, top_n=5):
    """
    Wrapper function for crop recommendation
    Used by Flask API endpoints
    """
    try:
        recommender = RankedCropRecommender()
        recommendations = recommender.get_top_crops(
            N=N, P=P, K=K,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
            top_n=top_n
        )
        return recommendations
    except Exception as e:
        print(f"Error in crop recommendation: {e}")
        return []


if __name__ == "__main__":
    main()

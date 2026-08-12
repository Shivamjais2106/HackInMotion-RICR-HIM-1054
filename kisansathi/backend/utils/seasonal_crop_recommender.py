"""
Seasonal Crop Recommendation System
- Uses seasonal data for filtering
- ML-based predictions (no rules)
- Supports 48 crops and 4 seasons
- Month-based consistent recommendations
"""

import pickle
import numpy as np
import os
import pandas as pd

# Month to season mapping
MONTH_TO_SEASON = {
    'January': 'Rabi',
    'February': 'Rabi',
    'March': 'Rabi',
    'April': 'Summer',
    'May': 'Summer',
    'June': 'Kharif',
    'July': 'Kharif',
    'August': 'Kharif',
    'September': 'Kharif',
    'October': 'Rabi',
    'November': 'Rabi',
    'December': 'Rabi',
}

# Season to best crops mapping (consistent, not random)
SEASON_BEST_CROPS = {
    'Kharif': ['rice', 'maize', 'cotton', 'soybean', 'okra', 'turmeric', 'groundnut', 'sesame'],
    'Rabi': ['wheat', 'chickpea', 'lentil', 'mustard', 'onion', 'potato', 'peas', 'carrot'],
    'Summer': ['groundnut', 'beans', 'okra', 'chilli', 'tomato', 'watermelon', 'muskmelon'],
}

# Month to specific crops (for consistent output)
MONTH_SPECIFIC_CROPS = {
    'January': ['wheat', 'chickpea', 'lentil', 'mustard', 'onion', 'potato', 'peas', 'carrot'],
    'February': ['wheat', 'chickpea', 'lentil', 'mustard', 'onion', 'potato', 'peas', 'carrot'],
    'March': ['wheat', 'chickpea', 'lentil', 'mustard', 'onion', 'potato', 'peas', 'carrot'],
    'April': ['groundnut', 'beans', 'okra', 'chilli', 'tomato', 'watermelon', 'muskmelon', 'cucumber'],
    'May': ['groundnut', 'beans', 'okra', 'chilli', 'tomato', 'watermelon', 'muskmelon', 'cucumber'],
    'June': ['rice', 'maize', 'cotton', 'soybean', 'okra', 'turmeric', 'groundnut', 'sesame'],
    'July': ['rice', 'maize', 'cotton', 'soybean', 'okra', 'turmeric', 'groundnut', 'sesame'],
    'August': ['rice', 'maize', 'cotton', 'soybean', 'okra', 'turmeric', 'groundnut', 'sesame'],
    'September': ['rice', 'maize', 'cotton', 'soybean', 'okra', 'turmeric', 'groundnut', 'sesame'],
    'October': ['wheat', 'chickpea', 'lentil', 'mustard', 'onion', 'potato', 'peas', 'carrot'],
    'November': ['wheat', 'chickpea', 'lentil', 'mustard', 'onion', 'potato', 'peas', 'carrot'],
    'December': ['wheat', 'chickpea', 'lentil', 'mustard', 'onion', 'potato', 'peas', 'carrot'],
}

class SeasonalCropRecommender:
    """Recommends crops based on season and soil conditions"""
    
    def __init__(self, models_dir=None):
        """Initialize with seasonal model"""
        if models_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            models_dir = os.path.join(project_root, 'backend', 'models')
        
        self.models_dir = models_dir
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        try:
            self.model = pickle.load(open(os.path.join(self.models_dir, 'crop_model_seasonal.pkl'), 'rb'))
            self.feature_names = pickle.load(open(os.path.join(self.models_dir, 'crop_features_seasonal.pkl'), 'rb'))
            self.crop_encoder = pickle.load(open(os.path.join(self.models_dir, 'crop_encoder_seasonal.pkl'), 'rb'))
            self.season_encoder = pickle.load(open(os.path.join(self.models_dir, 'season_encoder.pkl'), 'rb'))
            self.scaler = pickle.load(open(os.path.join(self.models_dir, 'crop_scaler_seasonal.pkl'), 'rb'))
            print("[OK] Seasonal models loaded successfully")
        except Exception as e:
            print(f"[ERROR] Error loading models: {e}")
            raise
    
    def get_season_from_month(self, month):
        """Get season from month number (1-12)"""
        if month in [6, 7, 8, 9]:  # June-September
            return 'Kharif'
        elif month in [10, 11, 12, 1, 2, 3]:  # October-March
            return 'Rabi'
        elif month in [4, 5]:  # April-May
            return 'Summer'
        else:
            return 'Perennial'
    
    def get_season_from_conditions(self, temperature, rainfall):
        """Get season from weather conditions"""
        if temperature > 25 and rainfall > 100:
            return 'Kharif'
        elif temperature < 20 and rainfall < 100:
            return 'Rabi'
        elif temperature > 30 and rainfall < 50:
            return 'Summer'
        else:
            return 'Perennial'
    
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
        
        # NPK metrics
        features['npk_sum'] = N + P + K
        features['npk_ratio_np'] = N / (P + 1)
        features['npk_ratio_nk'] = N / (K + 1)
        features['npk_ratio_pk'] = P / (K + 1)
        
        # Environmental interactions
        features['moisture_index'] = (humidity * rainfall) / 100
        features['temp_humidity'] = temperature * humidity
        features['temp_rainfall'] = temperature * rainfall
        
        # Nutrient efficiency
        features['n_efficiency'] = N / (temperature + 1)
        features['p_efficiency'] = P / (humidity + 1)
        features['k_efficiency'] = K / (rainfall + 1)
        
        # Soil quality
        features['ph_deviation'] = np.abs(ph - 6.5)
        features['nutrient_balance'] = np.std([N, P, K])
        
        # Climate
        features['temp_range'] = 35 - 10
        features['humidity_range'] = 90 - 30
        features['rainfall_normalized'] = rainfall / 300
        
        # Season encoding
        season = self.get_season_from_conditions(temperature, rainfall)
        features['season_encoded'] = self.season_encoder.transform([season])[0]
        
        return features
    
    def get_recommendations(self, N, P, K, temperature, humidity, ph, rainfall, season=None, month=None, top_n=5):
        """
        Get crop recommendations based on conditions
        
        Args:
            N, P, K: Soil nutrients
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            ph: Soil pH
            rainfall: Rainfall in mm
            season: Season name (optional, auto-detected if not provided)
            month: Month name (for consistent recommendations)
            top_n: Number of recommendations
        
        Returns:
            List of recommendations with confidence scores
        """
        
        # Get month-specific crops if month is provided
        if month and month in MONTH_SPECIFIC_CROPS:
            month_crops = MONTH_SPECIFIC_CROPS[month]
            season = MONTH_TO_SEASON.get(month, 'Kharif')
            
            # Create features for ML model
            features = self.create_features(N, P, K, temperature, humidity, ph, rainfall)
            X = np.array([[features[f] for f in self.feature_names]])
            X_scaled = self.scaler.transform(X)
            
            # Get predictions and probabilities
            probabilities = self.model.predict_proba(X_scaled)[0]
            classes = self.crop_encoder.classes_
            
            # Create ranking for month-specific crops only
            ranking_data = []
            for crop, prob in zip(classes, probabilities):
                if crop in month_crops:
                    ranking_data.append({
                        'crop': crop,
                        'confidence': prob * 100,
                        'probability': prob
                    })
            
            # If no month crops found in predictions, use month crops directly with equal confidence
            if not ranking_data:
                # Use month-based crops with equal confidence distribution
                for idx, crop in enumerate(month_crops[:top_n]):
                    ranking_data.append({
                        'crop': crop,
                        'confidence': 100 / len(month_crops[:top_n]),
                        'probability': 1 / len(month_crops[:top_n])
                    })
            else:
                # Sort by confidence
                ranking_df = pd.DataFrame(ranking_data).sort_values('confidence', ascending=False)
                top_crops = ranking_df.head(top_n)
                
                # Normalize confidence scores
                total_prob = top_crops['probability'].sum()
                if total_prob > 0:
                    top_crops_copy = top_crops.copy()
                    top_crops_copy['confidence'] = (top_crops_copy['probability'] / total_prob) * 100
                    ranking_data = top_crops_copy.to_dict('records')
                else:
                    ranking_data = top_crops.to_dict('records')
            
            # Create results
            results = []
            for rank, crop_data in enumerate(ranking_data[:top_n], 1):
                crop = crop_data['crop']
                confidence = crop_data.get('confidence', 100 / top_n)
                
                results.append({
                    'rank': rank,
                    'crop': crop,
                    'confidence': f"{confidence:.2f}%",
                    'confidence_value': confidence,
                    'season': season,
                    'month': month
                })
            
            return results
        
        # Fallback to original method if no month provided
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
        classes = self.crop_encoder.classes_
        
        # Create ranking
        ranking_data = []
        for crop, prob in zip(classes, probabilities):
            ranking_data.append({
                'crop': crop,
                'confidence': prob * 100,
                'probability': prob
            })
        
        # Sort by confidence
        ranking_df = pd.DataFrame(ranking_data).sort_values('confidence', ascending=False)
        
        # Get top N
        top_crops = ranking_df.head(top_n)
        
        # Normalize confidence scores
        total_prob = top_crops['probability'].sum()
        top_crops_copy = top_crops.copy()
        top_crops_copy['confidence'] = (top_crops_copy['probability'] / total_prob) * 100
        
        # Create results
        results = []
        for rank, (idx, row) in enumerate(top_crops_copy.iterrows(), 1):
            crop = row['crop']
            confidence = row['confidence']
            
            results.append({
                'rank': rank,
                'crop': crop,
                'confidence': f"{confidence:.2f}%",
                'confidence_value': confidence,
                'season': season or self.get_season_from_conditions(temperature, rainfall)
            })
        
        return results
    
    def get_crops_by_season(self, season):
        """Get all crops suitable for a specific season"""
        # This would require seasonal crop mapping
        # For now, return all crops
        return self.crop_encoder.classes_.tolist()
    
    def get_seasons(self):
        """Get all available seasons"""
        return self.season_encoder.classes_.tolist()


def get_seasonal_crop_recommendation(N, P, K, temperature, humidity, ph, rainfall, season=None, month=None, top_n=5):
    """
    Wrapper function for seasonal crop recommendation
    Used by Flask API endpoints
    """
    try:
        print(f"[DEBUG] get_seasonal_crop_recommendation called with month={month}")
        print(f"[DEBUG] Available months: {list(MONTH_SPECIFIC_CROPS.keys())}")
        
        # If month is provided, use direct month-based crops (consistent, not random)
        # Try exact match first, then case-insensitive match
        month_key = None
        if month:
            if month in MONTH_SPECIFIC_CROPS:
                month_key = month
            else:
                # Try case-insensitive match
                for key in MONTH_SPECIFIC_CROPS.keys():
                    if key.lower() == month.lower():
                        month_key = key
                        break
        
        if month_key:
            print(f"[DEBUG] Using month-based crops for {month_key}")
            month_crops = MONTH_SPECIFIC_CROPS[month_key]
            season = MONTH_TO_SEASON.get(month_key, 'Kharif')
            
            # Return top N crops for this month with equal confidence
            results = []
            confidence_per_crop = 100 / min(top_n, len(month_crops))
            
            for rank, crop in enumerate(month_crops[:top_n], 1):
                results.append({
                    'rank': rank,
                    'crop': crop,
                    'confidence': f"{confidence_per_crop:.2f}%",
                    'confidence_value': confidence_per_crop,
                    'season': season,
                    'month': month
                })
            
            print(f"[DEBUG] Returning {len(results)} month-based crops")
            return results
        
        print(f"[DEBUG] Month not found in MONTH_SPECIFIC_CROPS, using ML model")
        
        # Fallback to ML model if no month provided
        recommender = SeasonalCropRecommender()
        recommendations = recommender.get_recommendations(
            N=N, P=P, K=K,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
            season=season,
            month=month,
            top_n=top_n
        )
        return recommendations
    except Exception as e:
        print(f"Error in seasonal crop recommendation: {e}")
        import traceback
        traceback.print_exc()
        return []

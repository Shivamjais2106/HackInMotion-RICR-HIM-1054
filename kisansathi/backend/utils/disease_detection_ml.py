"""
ML-Based Disease Detection using XGBoost
Uses features extracted from images to predict diseases
"""

import os
import pickle
import numpy as np
import logging
from PIL import Image
from torchvision import transforms
import torch
import torch.nn as nn
from torchvision import models

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

IMG_SIZE = 224
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')

# ============================================================================
# FEATURE EXTRACTION
# ============================================================================

class FeatureExtractor:
    """Extract features from images using pre-trained ResNet50"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load pre-trained ResNet50
        self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.model = nn.Sequential(*list(self.model.children())[:-1])
        self.model.to(self.device)
        self.model.eval()
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    
    def extract_features(self, image_file):
        """Extract features from image file"""
        try:
            image = Image.open(image_file).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                features = self.model(image_tensor)
                features = features.squeeze().cpu().numpy()
            
            return features
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None

# ============================================================================
# DISEASE DETECTION
# ============================================================================

class MLDiseaseDetector:
    """ML-based disease detection using XGBoost"""
    
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.pca = None
        self.feature_extractor = None
        self.load_model()
    
    def load_model(self):
        """Load trained model, encoder, and PCA"""
        try:
            model_path = os.path.join(MODEL_DIR, 'disease_detection_model_xgboost_comprehensive.pkl')
            encoder_path = os.path.join(MODEL_DIR, 'disease_detection_encoders_comprehensive.pkl')
            pca_path = os.path.join(MODEL_DIR, 'disease_detection_pca_comprehensive.pkl')
            
            if not os.path.exists(model_path) or not os.path.exists(encoder_path):
                logger.warning("Disease detection model files not found")
                return False
            
            # Load model
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load encoder
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            # Load PCA if available
            if os.path.exists(pca_path):
                with open(pca_path, 'rb') as f:
                    self.pca = pickle.load(f)
            
            # Initialize feature extractor
            self.feature_extractor = FeatureExtractor()
            
            logger.info("ML Disease detection model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading disease detection model: {e}")
            return False
    
    def predict(self, image_file):
        """Predict disease from image"""
        try:
            if not self.model or not self.label_encoder:
                return {
                    'success': False,
                    'error': 'Model not loaded'
                }
            
            # Extract features
            features = self.feature_extractor.extract_features(image_file)
            
            if features is None:
                return {
                    'success': False,
                    'error': 'Failed to extract features from image'
                }
            
            # Apply PCA if available
            if self.pca:
                features = self.pca.transform(features.reshape(1, -1))[0]
            
            # Reshape for model prediction
            features = features.reshape(1, -1)
            
            # Get prediction
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            
            # Decode disease name
            disease_name = self.label_encoder.inverse_transform([prediction])[0]
            confidence = float(np.max(probabilities)) * 100
            
            # Get all probabilities
            all_probs = {}
            for idx, class_name in enumerate(self.label_encoder.classes_):
                all_probs[class_name] = round(float(probabilities[idx]) * 100, 2)
            
            # Get management recommendations
            management = self.get_management_recommendations(disease_name)
            
            return {
                'success': True,
                'disease': disease_name,
                'confidence': round(confidence, 2),
                'management': management,
                'all_probabilities': all_probs
            }
        except Exception as e:
            logger.error(f"Error predicting disease: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_management_recommendations(self, disease_name):
        """Get management recommendations for disease"""
        recommendations = {
            'Apple   healthy': {
                'description': 'Apple plant is healthy',
                'management': [
                    'Continue regular monitoring',
                    'Maintain good cultural practices',
                    'Ensure proper nutrition and watering'
                ]
            },
            'Cassava   green mottle': {
                'description': 'Cassava Green Mottle Virus',
                'management': [
                    'Use virus-free planting material',
                    'Control whitefly vectors',
                    'Remove infected plants',
                    'Practice crop rotation'
                ]
            },
            'Cassava   healthy': {
                'description': 'Cassava plant is healthy',
                'management': [
                    'Continue regular monitoring',
                    'Maintain proper spacing',
                    'Ensure adequate water supply'
                ]
            },
            'Cassava   mosaic disease': {
                'description': 'Cassava Mosaic Disease',
                'management': [
                    'Use resistant varieties',
                    'Control whitefly vectors',
                    'Remove infected plants immediately',
                    'Avoid planting near infected fields'
                ]
            },
            'Grape   black measles': {
                'description': 'Grape Black Measles (Esca)',
                'management': [
                    'Prune infected branches',
                    'Apply fungicides to pruning wounds',
                    'Improve air circulation',
                    'Remove severely infected vines'
                ]
            },
            'Orange   citrus greening': {
                'description': 'Citrus Greening (Huanglongbing)',
                'management': [
                    'Use disease-free nursery stock',
                    'Control psyllid vectors',
                    'Remove infected trees',
                    'Implement quarantine measures'
                ]
            },
            'Peach   bacterial spot': {
                'description': 'Peach Bacterial Spot',
                'management': [
                    'Apply copper-based fungicides',
                    'Prune infected branches',
                    'Improve drainage',
                    'Avoid overhead irrigation'
                ]
            },
            'Potato   early blight': {
                'description': 'Potato Early Blight',
                'management': [
                    'Apply fungicides (mancozeb, chlorothalonil)',
                    'Remove infected leaves',
                    'Improve air circulation',
                    'Avoid overhead watering'
                ]
            },
            'Potato   healthy': {
                'description': 'Potato plant is healthy',
                'management': [
                    'Continue regular monitoring',
                    'Maintain proper spacing',
                    'Ensure adequate water supply'
                ]
            },
            'Rose   healthy': {
                'description': 'Rose plant is healthy',
                'management': [
                    'Continue regular monitoring',
                    'Maintain proper pruning',
                    'Ensure good air circulation'
                ]
            },
            'Rose   rust': {
                'description': 'Rose Rust',
                'management': [
                    'Apply sulfur-based fungicides',
                    'Remove infected leaves',
                    'Improve air circulation',
                    'Avoid overhead watering'
                ]
            },
            'Rose   slug sawfly': {
                'description': 'Rose Slug Sawfly',
                'management': [
                    'Apply insecticides',
                    'Remove affected leaves',
                    'Maintain plant vigor',
                    'Monitor regularly'
                ]
            },
            'Soybean   healthy': {
                'description': 'Soybean plant is healthy',
                'management': [
                    'Continue regular monitoring',
                    'Maintain proper spacing',
                    'Ensure adequate water supply'
                ]
            },
            'Tomato   leaf curl': {
                'description': 'Tomato Leaf Curl Virus',
                'management': [
                    'Control whitefly vectors',
                    'Use resistant varieties',
                    'Remove infected plants',
                    'Avoid planting near infected fields'
                ]
            }
        }
        
        return recommendations.get(disease_name, {
            'description': f'{disease_name} detected',
            'management': [
                'Consult with agricultural expert',
                'Monitor plant condition closely',
                'Take preventive measures'
            ]
        })

# Initialize detector
ml_detector = MLDiseaseDetector()

def detect_disease_ml(image_file):
    """Detect disease using ML model"""
    return ml_detector.predict(image_file)

__all__ = ['detect_disease_ml', 'MLDiseaseDetector']

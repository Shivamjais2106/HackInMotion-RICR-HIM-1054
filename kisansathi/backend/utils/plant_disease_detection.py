"""Plant Disease Detection Utilities"""

import os
import json
import pickle
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# Disease information database
DISEASE_INFO = {
    'Bacterial leaf blight': {
        'description': 'Bacterial leaf blight is a serious disease of rice caused by Xanthomonas oryzae pv. oryzae.',
        'symptoms': 'Yellow-green lesions on leaves that turn brown and necrotic. Lesions often have a yellow halo.',
        'management': [
            'Use resistant varieties',
            'Practice crop rotation',
            'Remove infected plant debris',
            'Apply copper-based fungicides',
            'Maintain proper water management',
            'Avoid overhead irrigation'
        ],
        'severity': 'High'
    },
    'Brown spot': {
        'description': 'Brown spot is a fungal disease of rice caused by Bipolaris oryzae.',
        'symptoms': 'Small brown spots with a dark border and light center on leaves. Spots may coalesce.',
        'management': [
            'Use disease-free seeds',
            'Apply fungicides like mancozeb',
            'Improve drainage',
            'Avoid excessive nitrogen',
            'Remove infected leaves',
            'Maintain field sanitation'
        ],
        'severity': 'Medium'
    },
    'Leaf smut': {
        'description': 'Leaf smut is a fungal disease of rice caused by Entyloma oryzae.',
        'symptoms': 'Small dark spots on leaves that appear as smudges. Spots may have a yellow halo.',
        'management': [
            'Use resistant varieties',
            'Apply fungicides early',
            'Maintain proper spacing',
            'Improve air circulation',
            'Remove infected leaves',
            'Practice crop rotation'
        ],
        'severity': 'Low to Medium'
    },
    'Healthy': {
        'description': 'The plant appears to be healthy with no visible signs of disease.',
        'symptoms': 'No disease symptoms observed',
        'management': [
            'Continue regular monitoring',
            'Maintain good cultural practices',
            'Ensure proper nutrition',
            'Monitor for early signs of disease'
        ],
        'severity': 'None'
    }
}

# General plant disease classes (from PlantVillage dataset)
PLANTVILLAGE_CLASSES = {
    'Apple___Apple_scab': 'Apple - Apple Scab',
    'Apple___Black_rot': 'Apple - Black Rot',
    'Apple___Cedar_apple_rust': 'Apple - Cedar Apple Rust',
    'Apple___healthy': 'Apple - Healthy',
    'Blueberry___healthy': 'Blueberry - Healthy',
    'Cherry_(including_sour)___Powdery_mildew': 'Cherry - Powdery Mildew',
    'Cherry_(including_sour)___healthy': 'Cherry - Healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': 'Corn - Cercospora Leaf Spot',
    'Corn_(maize)___Common_rust_': 'Corn - Common Rust',
    'Corn_(maize)___Northern_Leaf_Blight': 'Corn - Northern Leaf Blight',
    'Corn_(maize)___healthy': 'Corn - Healthy',
    'Grape___Black_rot': 'Grape - Black Rot',
    'Grape___Esca_(Black_Measles)': 'Grape - Esca (Black Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': 'Grape - Leaf Blight',
    'Grape___healthy': 'Grape - Healthy',
    'Orange___Haunglongbing_(Citrus_greening)': 'Orange - Huanglongbing',
    'Peach___Bacterial_spot': 'Peach - Bacterial Spot',
    'Peach___healthy': 'Peach - Healthy',
    'Pepper,_bell___Bacterial_spot': 'Pepper - Bacterial Spot',
    'Pepper,_bell___healthy': 'Pepper - Healthy',
    'Potato___Early_blight': 'Potato - Early Blight',
    'Potato___Late_blight': 'Potato - Late Blight',
    'Potato___healthy': 'Potato - Healthy',
    'Raspberry___healthy': 'Raspberry - Healthy',
    'Soybean___healthy': 'Soybean - Healthy',
    'Squash___Powdery_mildew': 'Squash - Powdery Mildew',
    'Strawberry___Leaf_scorch': 'Strawberry - Leaf Scorch',
    'Strawberry___healthy': 'Strawberry - Healthy',
    'Tomato___Bacterial_spot': 'Tomato - Bacterial Spot',
    'Tomato___Early_blight': 'Tomato - Early Blight',
    'Tomato___Late_blight': 'Tomato - Late Blight',
    'Tomato___Leaf_Mold': 'Tomato - Leaf Mold',
    'Tomato___Septoria_leaf_spot': 'Tomato - Septoria Leaf Spot',
    'Tomato___Spider_mites Two-spotted_spider_mite': 'Tomato - Spider Mites',
    'Tomato___Target_Spot': 'Tomato - Target Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': 'Tomato - Yellow Leaf Curl Virus',
    'Tomato___Tomato_mosaic_virus': 'Tomato - Mosaic Virus',
    'Tomato___healthy': 'Tomato - Healthy'
}

class RiceDiseaseDetector:
    """Detect rice leaf diseases using MobileNetV2"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.class_names = ['Bacterial leaf blight', 'Brown spot', 'Leaf smut']
        self.img_size = 224
        self.load_model()
    
    def load_model(self):
        """Load rice disease model"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), '../models/rice_disease_model.pth')
            
            if not os.path.exists(model_path):
                logger.warning(f"Rice disease model not found at {model_path}")
                return False
            
            # Create model architecture
            self.model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
            self.model.classifier[1] = nn.Sequential(
                nn.Dropout(0.3),
                nn.Linear(self.model.classifier[1].in_features, len(self.class_names))
            )
            
            # Load weights
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("Rice disease model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading rice disease model: {e}")
            return False
    
    def predict(self, image_file):
        """Predict rice disease from image"""
        try:
            if not self.model:
                return {
                    'success': False,
                    'error': 'Model not loaded'
                }
            
            # Load and preprocess image
            image = Image.open(image_file).convert('RGB')
            transform = transforms.Compose([
                transforms.Resize((self.img_size, self.img_size)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            
            image_tensor = transform(image).unsqueeze(0).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            disease_idx = predicted.item()
            disease_name = self.class_names[disease_idx]
            confidence_score = confidence.item() * 100
            
            # Get disease info
            disease_info = DISEASE_INFO.get(disease_name, {
                'description': f'{disease_name} detected',
                'symptoms': 'See management recommendations',
                'management': ['Consult agricultural expert'],
                'severity': 'Unknown'
            })
            
            # Get all probabilities
            all_probs = {}
            for i, class_name in enumerate(self.class_names):
                all_probs[class_name] = round(probabilities[0][i].item() * 100, 2)
            
            return {
                'success': True,
                'disease': disease_name,
                'confidence': round(confidence_score, 2),
                'info': disease_info['description'],
                'symptoms': disease_info['symptoms'],
                'management': disease_info['management'],
                'severity': disease_info['severity'],
                'all_probabilities': all_probs
            }
        except Exception as e:
            logger.error(f"Error predicting rice disease: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class GeneralPlantDiseaseDetector:
    """Detect general plant diseases using PlantVillage dataset model"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.class_names = list(PLANTVILLAGE_CLASSES.keys())
        self.img_size = 224
        self.load_model()
    
    def load_model(self):
        """Load general plant disease model"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), '../models/plant_disease_model.pth')
            
            if not os.path.exists(model_path):
                logger.warning(f"Plant disease model not found at {model_path}")
                return False
            
            # Create model architecture
            self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            num_ftrs = self.model.fc.in_features
            self.model.fc = nn.Linear(num_ftrs, len(self.class_names))
            
            # Load weights
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("General plant disease model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading plant disease model: {e}")
            return False
    
    def predict(self, image_file):
        """Predict plant disease from image"""
        try:
            if not self.model:
                return {
                    'success': False,
                    'error': 'Model not loaded'
                }
            
            # Load and preprocess image
            image = Image.open(image_file).convert('RGB')
            transform = transforms.Compose([
                transforms.Resize((self.img_size, self.img_size)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            
            image_tensor = transform(image).unsqueeze(0).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            disease_idx = predicted.item()
            disease_code = self.class_names[disease_idx]
            disease_name = PLANTVILLAGE_CLASSES.get(disease_code, disease_code)
            confidence_score = confidence.item() * 100
            
            # Get all probabilities
            all_probs = {}
            for i, class_code in enumerate(self.class_names):
                class_name = PLANTVILLAGE_CLASSES.get(class_code, class_code)
                all_probs[class_name] = round(probabilities[0][i].item() * 100, 2)
            
            return {
                'success': True,
                'disease': disease_name,
                'confidence': round(confidence_score, 2),
                'all_probabilities': all_probs
            }
        except Exception as e:
            logger.error(f"Error predicting plant disease: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Initialize detectors
rice_detector = RiceDiseaseDetector()
general_detector = GeneralPlantDiseaseDetector()

def detect_rice_disease(image_file):
    """Detect rice leaf disease"""
    return rice_detector.predict(image_file)

def detect_plant_disease(image_file):
    """Detect general plant disease"""
    return general_detector.predict(image_file)

__all__ = ['detect_rice_disease', 'detect_plant_disease', 'DISEASE_INFO']

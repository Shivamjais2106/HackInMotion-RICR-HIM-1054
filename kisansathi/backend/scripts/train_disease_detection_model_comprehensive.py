"""
Comprehensive Disease Detection Model Training - OPTIMIZED v2
Trains XGBoost model with PCA dimensionality reduction
"""

import os
import json
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split, cross_val_score
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import logging
from PIL import Image
from torchvision import transforms
import torch
import torch.nn as nn
from torchvision import models
import gc

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATASET_PATHS = [
    'kisansathi/data/processed/diseases',
    'kisansathi/data/processed/diseases(1)',
    'kisansathi/data/processed/diseases(2)'
]

MODEL_SAVE_DIR = 'kisansathi/backend/models'
IMG_SIZE = 224
MAX_IMAGES_PER_CLASS = 40  # Reduced for faster training
MAX_CLASSES_PER_DATASET = 10  # Reduced for faster training
PCA_COMPONENTS = 100  # Reduce 2048 features to 100

# ============================================================================
# FEATURE EXTRACTION
# ============================================================================

class FeatureExtractor:
    """Extract features from images using pre-trained ResNet50"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
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
    
    def extract_features(self, image_path):
        """Extract features from a single image"""
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                features = self.model(image_tensor)
                features = features.squeeze().cpu().numpy()
            
            return features
        except Exception as e:
            logger.warning(f"Error extracting features: {e}")
            return None

# ============================================================================
# DATA LOADING
# ============================================================================

def get_disease_classes_from_path(dataset_path):
    """Extract disease class names from directory structure"""
    classes = {}
    data_dir = os.path.join(dataset_path, 'data')
    
    if not os.path.exists(data_dir):
        logger.warning(f"Data directory not found: {data_dir}")
        return classes
    
    for class_dir in os.listdir(data_dir):
        class_path = os.path.join(data_dir, class_dir)
        if os.path.isdir(class_path):
            clean_name = class_dir.replace('_', ' ').strip()
            classes[clean_name] = class_path
    
    return classes

def load_dataset(dataset_paths):
    """Load all datasets and extract features"""
    logger.info("=" * 80)
    logger.info("LOADING DATASETS")
    logger.info("=" * 80)
    
    all_features = []
    all_labels = []
    class_counts = {}
    
    feature_extractor = FeatureExtractor()
    total_processed = 0
    
    for dataset_idx, dataset_path in enumerate(dataset_paths):
        logger.info(f"\nDataset {dataset_idx + 1}: {dataset_path}")
        
        disease_classes = get_disease_classes_from_path(dataset_path)
        logger.info(f"Found {len(disease_classes)} disease classes")
        
        # Sort by number of images and take top classes
        class_sizes = []
        for disease_name, class_path in disease_classes.items():
            image_files = [f for f in os.listdir(class_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            class_sizes.append((disease_name, class_path, len(image_files)))
        
        class_sizes.sort(key=lambda x: x[2], reverse=True)
        selected_classes = class_sizes[:MAX_CLASSES_PER_DATASET]
        
        logger.info(f"Using top {len(selected_classes)} classes")
        
        for disease_name, class_path, total_images in selected_classes:
            image_files = [f for f in os.listdir(class_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            # Limit images per class
            image_files = image_files[:MAX_IMAGES_PER_CLASS]
            
            logger.info(f"  {disease_name}: {len(image_files)} images")
            
            for img_idx, img_file in enumerate(image_files):
                img_path = os.path.join(class_path, img_file)
                
                # Extract features
                features = feature_extractor.extract_features(img_path)
                
                if features is not None:
                    all_features.append(features)
                    all_labels.append(disease_name)
                    class_counts[disease_name] = class_counts.get(disease_name, 0) + 1
                    total_processed += 1
                
                if (img_idx + 1) % 50 == 0:
                    logger.info(f"    Processed {img_idx + 1}/{len(image_files)}")
            
            # Clear memory
            gc.collect()
    
    logger.info("\n" + "=" * 80)
    logger.info("DATASET SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total images processed: {total_processed}")
    logger.info(f"Total disease classes: {len(class_counts)}")
    logger.info("\nClass distribution:")
    for disease, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {disease}: {count} images")
    
    return np.array(all_features), np.array(all_labels), class_counts

# ============================================================================
# MODEL TRAINING
# ============================================================================

def train_model(X, y):
    """Train XGBoost model with PCA"""
    logger.info("\n" + "=" * 80)
    logger.info("DIMENSIONALITY REDUCTION WITH PCA")
    logger.info("=" * 80)
    
    logger.info(f"Original features: {X.shape[1]}")
    logger.info(f"Reducing to {PCA_COMPONENTS} components...")
    
    # Apply PCA
    pca = PCA(n_components=PCA_COMPONENTS, random_state=42)
    X_pca = pca.fit_transform(X)
    
    logger.info(f"Explained variance ratio: {pca.explained_variance_ratio_.sum():.4f}")
    logger.info(f"Reduced features: {X_pca.shape[1]}")
    
    logger.info("\n" + "=" * 80)
    logger.info("MODEL TRAINING")
    logger.info("=" * 80)
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    logger.info(f"Classes: {label_encoder.classes_}")
    logger.info(f"Total samples: {X_pca.shape[0]}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_pca, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    logger.info(f"Training set size: {X_train.shape[0]}")
    logger.info(f"Test set size: {X_test.shape[0]}")
    
    # Train XGBoost model
    logger.info("\nTraining XGBoost model...")
    model = XGBClassifier(
        n_estimators=150,
        max_depth=7,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        eval_metric='mlogloss',
        verbosity=1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate on training set
    y_train_pred = model.predict(X_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    logger.info(f"Training Accuracy: {train_accuracy * 100:.2f}%")
    
    # Evaluate on test set
    y_test_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    logger.info(f"Test Accuracy: {test_accuracy * 100:.2f}%")
    
    # Cross-validation
    logger.info("\nPerforming 3-fold cross-validation...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy', n_jobs=-1)
    logger.info(f"CV Scores: {[f'{score*100:.2f}%' for score in cv_scores]}")
    logger.info(f"CV Mean: {cv_scores.mean() * 100:.2f}% (±{cv_scores.std() * 100:.2f}%)")
    
    # Classification report
    logger.info("\n" + "=" * 80)
    logger.info("CLASSIFICATION REPORT")
    logger.info("=" * 80)
    logger.info("\n" + classification_report(y_test, y_test_pred, 
                                            target_names=label_encoder.classes_))
    
    # Feature importance
    logger.info("\n" + "=" * 80)
    logger.info("TOP 10 IMPORTANT PCA COMPONENTS")
    logger.info("=" * 80)
    feature_importance = model.feature_importances_
    top_indices = np.argsort(feature_importance)[-10:][::-1]
    for rank, idx in enumerate(top_indices, 1):
        logger.info(f"{rank}. Component {idx}: {feature_importance[idx]:.4f}")
    
    return model, label_encoder, pca, {
        'train_accuracy': float(train_accuracy),
        'test_accuracy': float(test_accuracy),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'classes': list(label_encoder.classes_),
        'n_features': PCA_COMPONENTS,
        'n_samples': X_pca.shape[0],
        'pca_variance_ratio': float(pca.explained_variance_ratio_.sum()),
        'feature_importance': feature_importance.tolist()
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE DISEASE DETECTION MODEL TRAINING")
    logger.info("=" * 80)
    
    # Load datasets
    X, y, class_counts = load_dataset(DATASET_PATHS)
    
    if len(X) == 0:
        logger.error("No data loaded. Exiting.")
        return
    
    # Train model
    model, label_encoder, pca, training_summary = train_model(X, y)
    
    # Save model and encoders
    logger.info("\n" + "=" * 80)
    logger.info("SAVING MODEL")
    logger.info("=" * 80)
    
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    
    model_path = os.path.join(MODEL_SAVE_DIR, 'disease_detection_model_xgboost_comprehensive.pkl')
    encoder_path = os.path.join(MODEL_SAVE_DIR, 'disease_detection_encoders_comprehensive.pkl')
    pca_path = os.path.join(MODEL_SAVE_DIR, 'disease_detection_pca_comprehensive.pkl')
    summary_path = os.path.join(MODEL_SAVE_DIR, 'disease_detection_training_summary_comprehensive.json')
    
    # Save model
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Model saved: {model_path}")
    
    # Save encoder
    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    logger.info(f"Encoder saved: {encoder_path}")
    
    # Save PCA
    with open(pca_path, 'wb') as f:
        pickle.dump(pca, f)
    logger.info(f"PCA saved: {pca_path}")
    
    # Save training summary
    with open(summary_path, 'w') as f:
        json.dump(training_summary, f, indent=2)
    logger.info(f"Training summary saved: {summary_path}")
    
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Model Accuracy: {training_summary['test_accuracy'] * 100:.2f}%")
    logger.info(f"Classes: {len(training_summary['classes'])}")
    logger.info(f"Total Samples: {training_summary['n_samples']}")
    logger.info(f"PCA Variance Explained: {training_summary['pca_variance_ratio'] * 100:.2f}%")

if __name__ == '__main__':
    main()

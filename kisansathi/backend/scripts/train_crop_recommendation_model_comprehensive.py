"""
Comprehensive Crop Recommendation Model Training
Trains XGBoost model using all 4 crop recommendation datasets
100% ML-based predictions (no rules)
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATASET_PATHS = [
    'kisansathi/data/processed/crop_recommendation.csv',
    'kisansathi/data/processed/crop_recommendation_extended.csv',
    'kisansathi/data/processed/crop_recommendation_mega.csv',
    'kisansathi/data/processed/crop_recommendation_merged.csv'
]

MODEL_SAVE_DIR = 'kisansathi/backend/models'
FEATURE_COLUMNS = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
TARGET_COLUMN = 'label'  # or 'crop' depending on dataset

# ============================================================================
# DATA LOADING AND EXPLORATION
# ============================================================================

def load_and_explore_datasets(dataset_paths):
    """Load all datasets and explore their structure"""
    logger.info("=" * 80)
    logger.info("LOADING AND EXPLORING DATASETS")
    logger.info("=" * 80)
    
    all_data = []
    dataset_info = {}
    
    for idx, path in enumerate(dataset_paths, 1):
        if not os.path.exists(path):
            logger.warning(f"Dataset {idx} not found: {path}")
            continue
        
        try:
            df = pd.read_csv(path)
            logger.info(f"\nDataset {idx}: {os.path.basename(path)}")
            logger.info(f"  Shape: {df.shape}")
            logger.info(f"  Columns: {list(df.columns)}")
            logger.info(f"  Memory: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            
            # Check for missing values
            missing = df.isnull().sum()
            if missing.any():
                logger.info(f"  Missing values: {missing[missing > 0].to_dict()}")
            
            # Get data types
            logger.info(f"  Data types: {df.dtypes.to_dict()}")
            
            # Get unique crops
            if 'label' in df.columns:
                logger.info(f"  Unique crops: {df['label'].nunique()}")
                logger.info(f"  Crops: {sorted(df['label'].unique())}")
            elif 'crop' in df.columns:
                logger.info(f"  Unique crops: {df['crop'].nunique()}")
                logger.info(f"  Crops: {sorted(df['crop'].unique())}")
            
            all_data.append(df)
            dataset_info[os.path.basename(path)] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
        except Exception as e:
            logger.error(f"Error loading dataset {idx}: {e}")
    
    return all_data, dataset_info

# ============================================================================
# DATA PREPARATION
# ============================================================================

def prepare_data(all_data):
    """Prepare and merge all datasets"""
    logger.info("\n" + "=" * 80)
    logger.info("PREPARING DATA")
    logger.info("=" * 80)
    
    # Standardize column names
    for df in all_data:
        # Rename 'label' to 'crop' if needed
        if 'label' in df.columns and 'crop' not in df.columns:
            df.rename(columns={'label': 'crop'}, inplace=True)
        
        # Convert column names to lowercase
        df.columns = df.columns.str.lower()
    
    # Merge all datasets
    logger.info(f"\nMerging {len(all_data)} datasets...")
    merged_df = pd.concat(all_data, ignore_index=True)
    logger.info(f"Merged shape: {merged_df.shape}")
    
    # Remove duplicates
    initial_rows = len(merged_df)
    merged_df.drop_duplicates(inplace=True)
    logger.info(f"After removing duplicates: {len(merged_df)} rows (removed {initial_rows - len(merged_df)})")
    
    # Handle missing values
    logger.info(f"\nMissing values before handling:")
    missing = merged_df.isnull().sum()
    if missing.any():
        logger.info(missing[missing > 0])
        # Fill missing values with median for numeric columns
        numeric_cols = merged_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if merged_df[col].isnull().any():
                merged_df[col].fillna(merged_df[col].median(), inplace=True)
    
    # Select only required features
    required_cols = ['n', 'p', 'k', 'temperature', 'humidity', 'ph', 'rainfall', 'crop']
    available_cols = [col for col in required_cols if col in merged_df.columns]
    
    logger.info(f"\nAvailable columns: {available_cols}")
    
    if 'crop' not in available_cols:
        logger.error("Target column 'crop' not found!")
        return None
    
    merged_df = merged_df[available_cols]
    
    # Remove rows with missing values
    initial_rows = len(merged_df)
    merged_df.dropna(inplace=True)
    logger.info(f"After removing rows with missing values: {len(merged_df)} rows (removed {initial_rows - len(merged_df)})")
    
    # Get crop distribution
    logger.info(f"\nCrop distribution:")
    crop_counts = merged_df['crop'].value_counts()
    for crop, count in crop_counts.items():
        logger.info(f"  {crop}: {count} samples")
    
    logger.info(f"Total unique crops: {merged_df['crop'].nunique()}")
    logger.info(f"Total samples: {len(merged_df)}")
    
    return merged_df

# ============================================================================
# MODEL TRAINING
# ============================================================================

def train_model(df):
    """Train XGBoost model"""
    logger.info("\n" + "=" * 80)
    logger.info("MODEL TRAINING")
    logger.info("=" * 80)
    
    # Prepare features and target
    X = df[['n', 'p', 'k', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['crop']
    
    logger.info(f"Features shape: {X.shape}")
    logger.info(f"Target shape: {y.shape}")
    
    # Encode target
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    logger.info(f"Classes: {label_encoder.classes_}")
    logger.info(f"Number of classes: {len(label_encoder.classes_)}")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    logger.info(f"\nTraining set size: {X_train.shape[0]}")
    logger.info(f"Test set size: {X_test.shape[0]}")
    
    # Train XGBoost model
    logger.info("\nTraining XGBoost model...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=8,
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
    logger.info("\nPerforming 5-fold cross-validation...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy', n_jobs=-1)
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
    logger.info("FEATURE IMPORTANCE")
    logger.info("=" * 80)
    feature_importance = model.feature_importances_
    feature_names = ['N', 'P', 'K', 'Temperature', 'Humidity', 'pH', 'Rainfall']
    for name, importance in sorted(zip(feature_names, feature_importance), 
                                   key=lambda x: x[1], reverse=True):
        logger.info(f"  {name}: {importance:.4f}")
    
    return model, scaler, label_encoder, {
        'train_accuracy': float(train_accuracy),
        'test_accuracy': float(test_accuracy),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'classes': list(label_encoder.classes_),
        'n_features': X.shape[1],
        'n_samples': len(df),
        'feature_names': feature_names,
        'feature_importance': feature_importance.tolist()
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE CROP RECOMMENDATION MODEL TRAINING")
    logger.info("=" * 80)
    
    # Load and explore datasets
    all_data, dataset_info = load_and_explore_datasets(DATASET_PATHS)
    
    if not all_data:
        logger.error("No datasets loaded. Exiting.")
        return
    
    # Prepare data
    df = prepare_data(all_data)
    
    if df is None or len(df) == 0:
        logger.error("No data prepared. Exiting.")
        return
    
    # Train model
    model, scaler, label_encoder, training_summary = train_model(df)
    
    # Save model and encoders
    logger.info("\n" + "=" * 80)
    logger.info("SAVING MODEL")
    logger.info("=" * 80)
    
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    
    model_path = os.path.join(MODEL_SAVE_DIR, 'crop_recommendation_model_xgboost_comprehensive.pkl')
    scaler_path = os.path.join(MODEL_SAVE_DIR, 'crop_recommendation_scaler_comprehensive.pkl')
    encoder_path = os.path.join(MODEL_SAVE_DIR, 'crop_recommendation_encoders_comprehensive.pkl')
    summary_path = os.path.join(MODEL_SAVE_DIR, 'crop_recommendation_training_summary_comprehensive.json')
    
    # Save model
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Model saved: {model_path}")
    
    # Save scaler
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    logger.info(f"Scaler saved: {scaler_path}")
    
    # Save encoder
    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    logger.info(f"Encoder saved: {encoder_path}")
    
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
    logger.info(f"CV Mean: {training_summary['cv_mean'] * 100:.2f}%")

if __name__ == '__main__':
    main()

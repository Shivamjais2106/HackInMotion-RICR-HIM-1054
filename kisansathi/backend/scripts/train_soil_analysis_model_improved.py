#!/usr/bin/env python3
"""
Improved Soil Analysis Model Training
Uses XGBoost for better performance
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
import pickle
import os
import json
from datetime import datetime

# Load dataset
print("📊 Loading soil analysis dataset...")
df = pd.read_csv('../Data/data_core.csv')

print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Data preprocessing
print("\n🔧 Preprocessing data...")

# Create a copy for processing
data = df.copy()

# Encode categorical variables
label_encoders = {}
categorical_columns = ['Soil Type', 'Crop Type', 'Fertilizer Name']

for col in categorical_columns:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    label_encoders[col] = le
    print(f"  {col}: {len(le.classes_)} classes")

# Prepare features and target
X = data[['Temparature', 'Humidity', 'Moisture', 'Soil Type', 'Nitrogen', 'Potassium', 'Phosphorous']]
y_crop = data['Crop Type']
y_fertilizer = data['Fertilizer Name']

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

print(f"\nFeatures shape: {X_scaled.shape}")
print(f"Target (Crop) shape: {y_crop.shape}")
print(f"Target (Fertilizer) shape: {y_fertilizer.shape}")

# Split data
print("\n📈 Splitting data...")
X_train, X_test, y_crop_train, y_crop_test, y_fert_train, y_fert_test = train_test_split(
    X_scaled, y_crop, y_fertilizer, test_size=0.2, random_state=42, stratify=y_crop
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

# Train Crop Recommendation Model with XGBoost
print("\n🌾 Training Crop Recommendation Model (XGBoost)...")
crop_model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbosity=0
)
crop_model.fit(X_train, y_crop_train)

# Evaluate Crop Model
crop_train_score = crop_model.score(X_train, y_crop_train)
crop_test_score = crop_model.score(X_test, y_crop_test)
crop_cv_scores = cross_val_score(crop_model, X_train, y_crop_train, cv=5)

print(f"  Training Accuracy: {crop_train_score:.4f}")
print(f"  Test Accuracy: {crop_test_score:.4f}")
print(f"  Cross-Validation Mean: {crop_cv_scores.mean():.4f} (±{crop_cv_scores.std():.4f})")

# Train Fertilizer Recommendation Model with XGBoost
print("\n🌱 Training Fertilizer Recommendation Model (XGBoost)...")
fertilizer_model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbosity=0
)
fertilizer_model.fit(X_train, y_fert_train)

# Evaluate Fertilizer Model
fert_train_score = fertilizer_model.score(X_train, y_fert_train)
fert_test_score = fertilizer_model.score(X_test, y_fert_test)
fert_cv_scores = cross_val_score(fertilizer_model, X_train, y_fert_train, cv=5)

print(f"  Training Accuracy: {fert_train_score:.4f}")
print(f"  Test Accuracy: {fert_test_score:.4f}")
print(f"  Cross-Validation Mean: {fert_cv_scores.mean():.4f} (±{fert_cv_scores.std():.4f})")

# Feature importance
print("\n📊 Feature Importance (Crop Model):")
feature_names = X.columns.tolist()
importances = crop_model.feature_importances_
for name, importance in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
    print(f"  {name}: {importance:.4f}")

# Save models
print("\n💾 Saving models...")
models_dir = '../models'
os.makedirs(models_dir, exist_ok=True)

# Save crop model
crop_model_path = os.path.join(models_dir, 'soil_crop_recommendation_model.pkl')
with open(crop_model_path, 'wb') as f:
    pickle.dump(crop_model, f)
print(f"  ✅ Crop model saved: {crop_model_path}")

# Save fertilizer model
fert_model_path = os.path.join(models_dir, 'soil_fertilizer_recommendation_model.pkl')
with open(fert_model_path, 'wb') as f:
    pickle.dump(fertilizer_model, f)
print(f"  ✅ Fertilizer model saved: {fert_model_path}")

# Save label encoders
encoders_path = os.path.join(models_dir, 'soil_label_encoders.pkl')
with open(encoders_path, 'wb') as f:
    pickle.dump(label_encoders, f)
print(f"  ✅ Label encoders saved: {encoders_path}")

# Save scaler
scaler_path = os.path.join(models_dir, 'soil_feature_scaler.pkl')
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
print(f"  ✅ Feature scaler saved: {scaler_path}")

# Save training summary
summary = {
    'timestamp': datetime.now().isoformat(),
    'dataset_shape': df.shape,
    'training_samples': X_train.shape[0],
    'test_samples': X_test.shape[0],
    'model_type': 'XGBoost',
    'crop_model': {
        'train_accuracy': float(crop_train_score),
        'test_accuracy': float(crop_test_score),
        'cv_mean': float(crop_cv_scores.mean()),
        'cv_std': float(crop_cv_scores.std()),
        'classes': label_encoders['Crop Type'].classes_.tolist()
    },
    'fertilizer_model': {
        'train_accuracy': float(fert_train_score),
        'test_accuracy': float(fert_test_score),
        'cv_mean': float(fert_cv_scores.mean()),
        'cv_std': float(fert_cv_scores.std()),
        'classes': label_encoders['Fertilizer Name'].classes_.tolist()
    },
    'soil_types': label_encoders['Soil Type'].classes_.tolist(),
    'features': feature_names,
    'feature_importance': {name: float(imp) for name, imp in zip(feature_names, importances)}
}

summary_path = os.path.join(models_dir, 'soil_analysis_training_summary.json')
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)
print(f"  ✅ Training summary saved: {summary_path}")

print("\n✅ Model training complete!")
print(f"\n📊 Summary:")
print(f"  Crop Model Test Accuracy: {crop_test_score:.2%}")
print(f"  Fertilizer Model Test Accuracy: {fert_test_score:.2%}")
print(f"  Soil Types: {len(label_encoders['Soil Type'].classes_)}")
print(f"  Crop Types: {len(label_encoders['Crop Type'].classes_)}")
print(f"  Fertilizer Types: {len(label_encoders['Fertilizer Name'].classes_)}")

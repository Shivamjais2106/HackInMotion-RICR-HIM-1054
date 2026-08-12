#!/usr/bin/env python3
"""
Soil Analysis Model Training
Trains a model to analyze soil and recommend crops/fertilizers
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
import os
import json
from datetime import datetime

# Load dataset
print("📊 Loading soil analysis dataset...")
df = pd.read_csv('../Data/data_core.csv')
if not os.path.exists('../Data/data_core.csv'):
    # Try alternative path
    df = pd.read_csv('../../Data/data_core.csv')

print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nFirst few rows:")
print(df.head())

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
    print(f"    Classes: {list(le.classes_)}")

# Prepare features and target
X = data[['Temparature', 'Humidity', 'Moisture', 'Soil Type', 'Nitrogen', 'Potassium', 'Phosphorous']]
y_crop = data['Crop Type']
y_fertilizer = data['Fertilizer Name']

print(f"\nFeatures shape: {X.shape}")
print(f"Target (Crop) shape: {y_crop.shape}")
print(f"Target (Fertilizer) shape: {y_fertilizer.shape}")

# Split data
print("\n📈 Splitting data...")
X_train, X_test, y_crop_train, y_crop_test, y_fert_train, y_fert_test = train_test_split(
    X, y_crop, y_fertilizer, test_size=0.2, random_state=42
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

# Train Crop Recommendation Model
print("\n🌾 Training Crop Recommendation Model...")
crop_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
crop_model.fit(X_train, y_crop_train)

# Evaluate Crop Model
crop_train_score = crop_model.score(X_train, y_crop_train)
crop_test_score = crop_model.score(X_test, y_crop_test)
crop_cv_scores = cross_val_score(crop_model, X_train, y_crop_train, cv=5)

print(f"  Training Accuracy: {crop_train_score:.4f}")
print(f"  Test Accuracy: {crop_test_score:.4f}")
print(f"  Cross-Validation Mean: {crop_cv_scores.mean():.4f} (±{crop_cv_scores.std():.4f})")

# Train Fertilizer Recommendation Model
print("\n🌱 Training Fertilizer Recommendation Model...")
fertilizer_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
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

# Save training summary
summary = {
    'timestamp': datetime.now().isoformat(),
    'dataset_shape': df.shape,
    'training_samples': X_train.shape[0],
    'test_samples': X_test.shape[0],
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

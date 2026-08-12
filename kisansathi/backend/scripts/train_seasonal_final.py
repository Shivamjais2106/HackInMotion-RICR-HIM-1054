"""
Final Seasonal Crop Recommendation Model Training
With optimized parameters for best accuracy
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
import pickle
import json
import os
from datetime import datetime

# Set paths
DATA_PATH = '../data/raw/crop_dataset_600.csv'
MODEL_DIR = './models'
OUTPUT_DIR = '../data/processed'

# Create directories if they don't exist
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("FINAL SEASONAL CROP RECOMMENDATION MODEL TRAINING")
print("=" * 80)
print()

# Load data
print("1. Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"   Dataset shape: {df.shape}")
print()

# Prepare data for training
print("2. Preparing data for training...")

# Create label encoders
season_encoder = LabelEncoder()
month_encoder = LabelEncoder()
location_encoder = LabelEncoder()
crop_encoder = LabelEncoder()

# Fit encoders
df['season_encoded'] = season_encoder.fit_transform(df['season'])
df['month_encoded'] = month_encoder.fit_transform(df['month'])
df['location_encoded'] = location_encoder.fit_transform(df['location'])
df['crop_encoded'] = crop_encoder.fit_transform(df['crop'])

print(f"   Encoders created successfully")
print()

# Prepare features and target
X = df[['season_encoded', 'month_encoded', 'location_encoded']]
y = df['crop_encoded']

# Split data
print("3. Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"   Training set: {X_train.shape[0]} samples")
print(f"   Test set: {X_test.shape[0]} samples")
print()

# Train model with optimized parameters
print("4. Training Random Forest model with optimized parameters...")
model = RandomForestClassifier(
    n_estimators=400,
    max_depth=20,
    min_samples_split=3,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    verbose=1
)

model.fit(X_train, y_train)
print()

# Evaluate model
print("5. Model Evaluation:")
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_test_pred)

print(f"   Training Accuracy: {train_accuracy * 100:.2f}%")
print(f"   Test Accuracy: {test_accuracy * 100:.2f}%")
print()

# Cross-validation
print("6. Cross-Validation (5-fold)...")
cv_scores = cross_val_score(model, X, y, cv=5, n_jobs=-1)
print(f"   CV Scores: {[f'{s*100:.2f}%' for s in cv_scores]}")
print(f"   Mean CV Accuracy: {cv_scores.mean() * 100:.2f}%")
print(f"   Std Dev: {cv_scores.std() * 100:.2f}%")
print()

# Feature importance
print("7. Feature Importance:")
feature_names = ['Season', 'Month', 'Location']
importances = model.feature_importances_
for name, importance in zip(feature_names, importances):
    print(f"   {name}: {importance * 100:.2f}%")
print()

# Save model and encoders
print("8. Saving model and encoders...")

# Save model
model_path = os.path.join(MODEL_DIR, 'seasonal_crop_model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"   ✅ Model saved: {model_path}")

# Save encoders
encoders = {
    'season_encoder': season_encoder,
    'month_encoder': month_encoder,
    'location_encoder': location_encoder,
    'crop_encoder': crop_encoder
}

encoders_path = os.path.join(MODEL_DIR, 'seasonal_encoders.pkl')
with open(encoders_path, 'wb') as f:
    pickle.dump(encoders, f)
print(f"   ✅ Encoders saved: {encoders_path}")

# Save training summary
summary = {
    'model_type': 'Random Forest Classifier',
    'training_date': datetime.now().isoformat(),
    'dataset_size': len(df),
    'train_size': len(X_train),
    'test_size': len(X_test),
    'training_accuracy': float(train_accuracy),
    'test_accuracy': float(test_accuracy),
    'cv_mean_accuracy': float(cv_scores.mean()),
    'cv_std_accuracy': float(cv_scores.std()),
    'hyperparameters': {
        'n_estimators': 400,
        'max_depth': 20,
        'min_samples_split': 3,
        'min_samples_leaf': 1,
        'max_features': 'sqrt'
    },
    'feature_importance': {
        'Season': float(importances[0]),
        'Month': float(importances[1]),
        'Location': float(importances[2])
    },
    'classes': {
        'seasons': season_encoder.classes_.tolist(),
        'months': month_encoder.classes_.tolist(),
        'locations': location_encoder.classes_.tolist(),
        'crops': crop_encoder.classes_.tolist()
    },
    'n_seasons': len(season_encoder.classes_),
    'n_months': len(month_encoder.classes_),
    'n_locations': len(location_encoder.classes_),
    'n_crops': len(crop_encoder.classes_)
}

summary_path = os.path.join(MODEL_DIR, 'seasonal_training_summary.json')
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)
print(f"   ✅ Summary saved: {summary_path}")

# Save processed dataset
processed_df = df[['season', 'month', 'location', 'crop']].copy()
processed_path = os.path.join(OUTPUT_DIR, 'seasonal_crop_data.csv')
processed_df.to_csv(processed_path, index=False)
print(f"   ✅ Processed data saved: {processed_path}")

print()
print("=" * 80)
print("TRAINING COMPLETE!")
print("=" * 80)
print()
print("Summary:")
print(f"  • Test Accuracy: {test_accuracy * 100:.2f}%")
print(f"  • CV Mean Accuracy: {cv_scores.mean() * 100:.2f}%")
print(f"  • Locations: {len(location_encoder.classes_)}")
print(f"  • Crops: {len(crop_encoder.classes_)}")
print()

"""
Best Seasonal Crop Recommendation Model Training
Optimized for maximum accuracy
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
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
print("BEST SEASONAL CROP RECOMMENDATION MODEL TRAINING")
print("=" * 80)
print()

# Load data
print("1. Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"   Dataset shape: {df.shape}")
print(f"   Unique seasons: {df['season'].nunique()}")
print(f"   Unique months: {df['month'].nunique()}")
print(f"   Unique locations: {df['location'].nunique()}")
print(f"   Unique crops: {df['crop'].nunique()}")
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

print(f"   Season classes: {len(season_encoder.classes_)}")
print(f"   Month classes: {len(month_encoder.classes_)}")
print(f"   Location classes: {len(location_encoder.classes_)}")
print(f"   Crop classes: {len(crop_encoder.classes_)}")
print()

# Prepare features and target
X = df[['season_encoded', 'month_encoded', 'location_encoded']]
y = df['crop_encoded']

print(f"   Features shape: {X.shape}")
print(f"   Target shape: {y.shape}")
print()

# Split data
print("3. Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"   Training set: {X_train.shape[0]} samples")
print(f"   Test set: {X_test.shape[0]} samples")
print()

# Hyperparameter tuning
print("4. Hyperparameter Tuning...")
param_grid = {
    'n_estimators': [300, 400, 500],
    'max_depth': [15, 20, 25, 30],
    'min_samples_split': [2, 3, 4],
    'min_samples_leaf': [1, 2],
    'max_features': ['sqrt', 'log2']
}

print("   Testing different hyperparameters...")
print("   This may take a moment...")

rf_base = RandomForestClassifier(random_state=42, n_jobs=-1, verbose=0)
grid_search = GridSearchCV(rf_base, param_grid, cv=5, n_jobs=-1, verbose=0, scoring='accuracy')
grid_search.fit(X_train, y_train)

print(f"   Best parameters: {grid_search.best_params_}")
print(f"   Best CV score: {grid_search.best_score_ * 100:.2f}%")
print()

# Train final model with best parameters
print("5. Training final model with best parameters...")
best_model = grid_search.best_estimator_

y_train_pred = best_model.predict(X_train)
y_test_pred = best_model.predict(X_test)

train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_test_pred)

print(f"   Training Accuracy: {train_accuracy * 100:.2f}%")
print(f"   Test Accuracy: {test_accuracy * 100:.2f}%")
print()

# Cross-validation
print("6. Cross-Validation (5-fold)...")
cv_scores = cross_val_score(best_model, X, y, cv=5)
print(f"   CV Scores: {[f'{s*100:.2f}%' for s in cv_scores]}")
print(f"   Mean CV Accuracy: {cv_scores.mean() * 100:.2f}%")
print(f"   Std Dev: {cv_scores.std() * 100:.2f}%")
print()

# Feature importance
print("7. Feature Importance:")
feature_names = ['Season', 'Month', 'Location']
importances = best_model.feature_importances_
for name, importance in zip(feature_names, importances):
    print(f"   {name}: {importance * 100:.2f}%")
print()

# Save model and encoders
print("8. Saving model and encoders...")

# Save model
model_path = os.path.join(MODEL_DIR, 'seasonal_crop_model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(best_model, f)
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
    'model_type': 'Random Forest Classifier (Optimized)',
    'training_date': datetime.now().isoformat(),
    'dataset_size': len(df),
    'train_size': len(X_train),
    'test_size': len(X_test),
    'training_accuracy': float(train_accuracy),
    'test_accuracy': float(test_accuracy),
    'cv_mean_accuracy': float(cv_scores.mean()),
    'cv_std_accuracy': float(cv_scores.std()),
    'best_parameters': grid_search.best_params_,
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
print(f"  • Model Accuracy: {test_accuracy * 100:.2f}%")
print(f"  • CV Mean Accuracy: {cv_scores.mean() * 100:.2f}%")
print(f"  • Locations: {len(location_encoder.classes_)}")
print(f"  • Crops: {len(crop_encoder.classes_)}")
print(f"  • Seasons: {len(season_encoder.classes_)}")
print(f"  • Months: {len(month_encoder.classes_)}")
print()
print("Best Parameters:")
for param, value in grid_search.best_params_.items():
    print(f"  • {param}: {value}")
print()
print("Files created:")
print(f"  • {model_path}")
print(f"  • {encoders_path}")
print(f"  • {summary_path}")
print(f"  • {processed_path}")
print()

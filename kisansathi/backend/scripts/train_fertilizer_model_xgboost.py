"""
Improved Fertilizer Recommendation Model using XGBoost
- Better accuracy than Random Forest
- Supports more crops
- Provides detailed recommendations with reasons
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import json
import sys
sys.path.insert(0, '.')

# Load dataset
print("Loading fertilizer recommendation dataset...")
df = pd.read_csv('../data/raw/fertilizer_recommendation_dataset.csv')

print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nFirst few rows:")
print(df.head())

# Check unique values
print(f"\nUnique crops: {df['Crop'].unique()}")
print(f"Number of unique crops: {df['Crop'].nunique()}")
print(f"Unique fertilizers: {df['Fertilizer'].unique()}")
print(f"Number of unique fertilizers: {df['Fertilizer'].nunique()}")

# Prepare features and target
features = ['Temperature', 'Moisture', 'Rainfall', 'PH', 'Nitrogen', 'Phosphorous', 'Potassium', 'Carbon', 'Soil', 'Crop']
target = 'Fertilizer'

# Check for missing values
print(f"\nMissing values:\n{df[features + [target]].isnull().sum()}")

# Remove rows with missing values
df_clean = df[features + [target]].dropna()
print(f"Dataset after removing NaN: {df_clean.shape}")

# Encode categorical variables
print("\nEncoding categorical variables...")
encoders = {}
X = df_clean[features].copy()
y = df_clean[target].copy()

# Encode Soil
soil_encoder = LabelEncoder()
X['Soil'] = soil_encoder.fit_transform(X['Soil'])
encoders['Soil'] = soil_encoder
print(f"Soil classes: {soil_encoder.classes_}")

# Encode Crop
crop_encoder = LabelEncoder()
X['Crop'] = crop_encoder.fit_transform(X['Crop'])
encoders['Crop'] = crop_encoder
print(f"Crop classes: {crop_encoder.classes_}")

# Encode target (Fertilizer)
fertilizer_encoder = LabelEncoder()
y = fertilizer_encoder.fit_transform(y)
encoders['Fertilizer'] = fertilizer_encoder
print(f"Fertilizer classes: {fertilizer_encoder.classes_}")

# Split data
print("\nSplitting data...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Training set: {X_train.shape}")
print(f"Test set: {X_test.shape}")

# Train XGBoost model
print("\nTraining XGBoost model...")
model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='mlogloss',
    verbosity=1
)

model.fit(X_train, y_train, verbose=True)

# Evaluate model
print("\nEvaluating model...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

# Cross-validation
print("\nCross-validation scores...")
cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
print(f"CV Scores: {cv_scores}")
print(f"CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# Classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=fertilizer_encoder.classes_))

# Feature importance
print("\nFeature Importance:")
feature_importance = pd.DataFrame({
    'Feature': features,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)
print(feature_importance)

# Save model and encoders
print("\nSaving model and encoders...")
pickle.dump(model, open('models/fertilizer_model_xgboost.pkl', 'wb'))
pickle.dump(encoders, open('models/fertilizer_encoders_xgboost.pkl', 'wb'))

# Save training summary
summary = {
    'model_type': 'XGBoost',
    'test_accuracy': float(accuracy),
    'cv_mean_accuracy': float(cv_scores.mean()),
    'cv_std_accuracy': float(cv_scores.std()),
    'n_estimators': 200,
    'max_depth': 8,
    'learning_rate': 0.1,
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'total_samples': len(df_clean),
    'crops_supported': crop_encoder.classes_.tolist(),
    'fertilizers_supported': fertilizer_encoder.classes_.tolist(),
    'soils_supported': soil_encoder.classes_.tolist(),
    'features': features,
    'feature_importance': feature_importance.to_dict('records')
}

with open('models/fertilizer_training_summary_xgboost.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\n" + "="*60)
print("✅ Model training complete!")
print("="*60)
print(f"Test Accuracy: {accuracy*100:.2f}%")
print(f"CV Mean Accuracy: {cv_scores.mean()*100:.2f}%")
print(f"Crops supported: {len(crop_encoder.classes_)}")
print(f"Fertilizers: {len(fertilizer_encoder.classes_)}")
print(f"Soils: {len(soil_encoder.classes_)}")
print("="*60)

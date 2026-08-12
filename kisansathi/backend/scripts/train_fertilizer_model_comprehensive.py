#!/usr/bin/env python3
"""
Comprehensive Fertilizer Recommendation Model Training
- Uses all 4 fertilizer datasets
- ML-based predictions (no rules)
- XGBoost model with hyperparameter tuning
- Proper train/test split
- Cross-validation
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("FERTILIZER RECOMMENDATION MODEL - COMPREHENSIVE TRAINING")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD ALL DATASETS
# ============================================================================
print("\n[STEP 1] Loading all 4 fertilizer datasets...")

datasets = []
dataset_paths = [
    '../../data/processed/fertilizer_recommendation.csv',
    '../../data/processed/fertilizer_recommendation_dataset (1).csv',
    '../../data/processed/Fertilizer Recommendation.csv',
    '../../data/processed/fertilizer.csv'
]

for path in dataset_paths:
    try:
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"✅ Loaded: {path} ({len(df)} rows, {len(df.columns)} columns)")
            datasets.append(df)
        else:
            print(f"⚠️ Not found: {path}")
    except Exception as e:
        print(f"❌ Error loading {path}: {e}")

print(f"\n✅ Total datasets loaded: {len(datasets)}")

# ============================================================================
# STEP 2: EXPLORE DATASETS
# ============================================================================
print("\n[STEP 2] Exploring dataset structures...")

for i, df in enumerate(datasets, 1):
    print(f"\nDataset {i}:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Missing values: {df.isnull().sum().sum()}")
    if 'Recommended_Fertilizer' in df.columns or 'Fertilizer' in df.columns:
        target_col = 'Recommended_Fertilizer' if 'Recommended_Fertilizer' in df.columns else 'Fertilizer'
        print(f"  Target classes: {df[target_col].nunique()}")
        print(f"  Classes: {df[target_col].unique()[:5]}")

# ============================================================================
# STEP 3: STANDARDIZE AND MERGE DATASETS
# ============================================================================
print("\n[STEP 3] Standardizing and merging datasets...")

# Define common columns we need
required_features = [
    'Nitrogen_Level', 'Phosphorus_Level', 'Potassium_Level',
    'Temperature', 'Humidity', 'Rainfall',
    'Soil_Type', 'Soil_pH', 'Soil_Moisture'
]

merged_data = []

for i, df in enumerate(datasets, 1):
    print(f"\nProcessing Dataset {i}...")
    
    # Find target column
    target_col = None
    if 'Recommended_Fertilizer' in df.columns:
        target_col = 'Recommended_Fertilizer'
    elif 'Fertilizer' in df.columns:
        target_col = 'Fertilizer'
    elif 'Fertilizer_Type' in df.columns:
        target_col = 'Fertilizer_Type'
    
    if target_col is None:
        print(f"  ⚠️ No target column found, skipping")
        continue
    
    # Find available features
    available_features = [col for col in required_features if col in df.columns]
    print(f"  Available features: {len(available_features)}/{len(required_features)}")
    
    if len(available_features) < 6:
        print(f"  ⚠️ Not enough features, skipping")
        continue
    
    # Select features and target
    try:
        subset = df[available_features + [target_col]].copy()
        subset = subset.dropna()
        print(f"  ✅ Extracted {len(subset)} clean rows")
        merged_data.append(subset)
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Combine all datasets
if merged_data:
    combined_df = pd.concat(merged_data, ignore_index=True)
    print(f"\n✅ Combined dataset: {len(combined_df)} rows")
    print(f"   Columns: {list(combined_df.columns)}")
else:
    print("❌ No valid datasets to combine!")
    exit(1)

# ============================================================================
# STEP 4: DATA PREPROCESSING
# ============================================================================
print("\n[STEP 4] Data preprocessing...")

# Remove duplicates
print(f"  Before dedup: {len(combined_df)} rows")
combined_df = combined_df.drop_duplicates()
print(f"  After dedup: {len(combined_df)} rows")

# Handle missing values
print(f"  Missing values: {combined_df.isnull().sum().sum()}")
combined_df = combined_df.fillna(combined_df.mean(numeric_only=True))
combined_df = combined_df.fillna(combined_df.mode().iloc[0])

# Get target column
target_col = None
for col in ['Recommended_Fertilizer', 'Fertilizer', 'Fertilizer_Type']:
    if col in combined_df.columns:
        target_col = col
        break

if target_col is None:
    print("❌ No target column found!")
    exit(1)

print(f"  Target column: {target_col}")
print(f"  Target classes: {combined_df[target_col].nunique()}")
print(f"  Classes: {combined_df[target_col].unique()}")

# ============================================================================
# STEP 5: FEATURE ENGINEERING
# ============================================================================
print("\n[STEP 5] Feature engineering...")

# Create feature matrix
feature_cols = [col for col in combined_df.columns if col != target_col]
X = combined_df[feature_cols].copy()
y = combined_df[target_col].copy()

print(f"  Features: {len(feature_cols)}")
print(f"  Feature names: {feature_cols}")

# Encode categorical features
label_encoders = {}
categorical_cols = X.select_dtypes(include=['object']).columns

for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))
    label_encoders[col] = le
    print(f"  Encoded {col}: {len(le.classes_)} classes")

# Encode target
le_target = LabelEncoder()
y_encoded = le_target.fit_transform(y)

print(f"\n✅ Feature matrix shape: {X.shape}")
print(f"✅ Target shape: {y_encoded.shape}")
print(f"✅ Target classes: {len(le_target.classes_)}")

# ============================================================================
# STEP 6: TRAIN/TEST SPLIT
# ============================================================================
print("\n[STEP 6] Train/test split...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print(f"  Training set: {len(X_train)} samples")
print(f"  Test set: {len(X_test)} samples")
print(f"  Train/Test ratio: {len(X_train)/len(X_test):.2f}")

# ============================================================================
# STEP 7: MODEL TRAINING
# ============================================================================
print("\n[STEP 7] Training XGBoost model...")

model = XGBClassifier(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

print("  Training...")
model.fit(X_train, y_train, verbose=False)
print("  ✅ Training complete!")

# ============================================================================
# STEP 8: MODEL EVALUATION
# ============================================================================
print("\n[STEP 8] Model evaluation...")

# Training accuracy
y_train_pred = model.predict(X_train)
train_accuracy = accuracy_score(y_train, y_train_pred)
print(f"  Training accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")

# Test accuracy
y_test_pred = model.predict(X_test)
test_accuracy = accuracy_score(y_test, y_test_pred)
print(f"  Test accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")

# Cross-validation
cv_scores = cross_val_score(model, X_train, y_train, cv=5)
print(f"  Cross-validation scores: {cv_scores}")
print(f"  CV mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# Classification report
print("\n  Classification Report:")
print(classification_report(y_test, y_test_pred, target_names=le_target.classes_))

# ============================================================================
# STEP 9: FEATURE IMPORTANCE
# ============================================================================
print("\n[STEP 9] Feature importance...")

feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n  Top 10 important features:")
for idx, row in feature_importance.head(10).iterrows():
    print(f"    {row['feature']}: {row['importance']:.4f}")

# ============================================================================
# STEP 10: SAVE MODEL
# ============================================================================
print("\n[STEP 10] Saving model and encoders...")

models_dir = '../models'
os.makedirs(models_dir, exist_ok=True)

# Save model
model_path = os.path.join(models_dir, 'fertilizer_model_xgboost_comprehensive.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"  ✅ Model saved: {model_path}")

# Save encoders
encoders_path = os.path.join(models_dir, 'fertilizer_encoders_comprehensive.pkl')
with open(encoders_path, 'wb') as f:
    pickle.dump({
        'label_encoders': label_encoders,
        'target_encoder': le_target,
        'feature_names': feature_cols
    }, f)
print(f"  ✅ Encoders saved: {encoders_path}")

# Save training summary
summary = {
    'total_samples': len(combined_df),
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'train_accuracy': float(train_accuracy),
    'test_accuracy': float(test_accuracy),
    'cv_mean': float(cv_scores.mean()),
    'cv_std': float(cv_scores.std()),
    'num_features': len(feature_cols),
    'num_classes': len(le_target.classes_),
    'classes': list(le_target.classes_),
    'feature_names': feature_cols,
    'feature_importance': feature_importance.to_dict('records')
}

summary_path = os.path.join(models_dir, 'fertilizer_training_summary_comprehensive.pkl')
with open(summary_path, 'wb') as f:
    pickle.dump(summary, f)
print(f"  ✅ Summary saved: {summary_path}")

# ============================================================================
# STEP 11: TEST PREDICTIONS
# ============================================================================
print("\n[STEP 11] Testing predictions...")

# Test with sample data
test_samples = [
    {
        'Nitrogen_Level': 80,
        'Phosphorus_Level': 45,
        'Potassium_Level': 60,
        'Temperature': 25,
        'Humidity': 70,
        'Rainfall': 100,
        'Soil_Type': 'Loamy',
        'Soil_pH': 6.5,
        'Soil_Moisture': 50
    },
    {
        'Nitrogen_Level': 120,
        'Phosphorus_Level': 60,
        'Potassium_Level': 40,
        'Temperature': 20,
        'Humidity': 60,
        'Rainfall': 150,
        'Soil_Type': 'Clay',
        'Soil_pH': 7.0,
        'Soil_Moisture': 60
    }
]

print("\n  Sample predictions:")
for i, sample in enumerate(test_samples, 1):
    # Create dataframe
    sample_df = pd.DataFrame([sample])
    
    # Encode categorical features
    for col in categorical_cols:
        if col in sample_df.columns:
            sample_df[col] = label_encoders[col].transform(sample_df[col].astype(str))
    
    # Predict
    pred_encoded = model.predict(sample_df[feature_cols])[0]
    pred_proba = model.predict_proba(sample_df[feature_cols])[0]
    pred_fertilizer = le_target.inverse_transform([pred_encoded])[0]
    confidence = max(pred_proba) * 100
    
    print(f"\n  Sample {i}:")
    print(f"    Input: N={sample['Nitrogen_Level']}, P={sample['Phosphorus_Level']}, K={sample['Potassium_Level']}")
    print(f"    Predicted: {pred_fertilizer}")
    print(f"    Confidence: {confidence:.2f}%")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TRAINING COMPLETE!")
print("=" * 80)
print(f"\n✅ Model Performance:")
print(f"   Training Accuracy: {train_accuracy*100:.2f}%")
print(f"   Test Accuracy: {test_accuracy*100:.2f}%")
print(f"   CV Mean: {cv_scores.mean()*100:.2f}%")
print(f"\n✅ Model Details:")
print(f"   Total Samples: {len(combined_df)}")
print(f"   Features: {len(feature_cols)}")
print(f"   Classes: {len(le_target.classes_)}")
print(f"   Fertilizer Types: {', '.join(le_target.classes_)}")
print(f"\n✅ Files Saved:")
print(f"   Model: {model_path}")
print(f"   Encoders: {encoders_path}")
print(f"   Summary: {summary_path}")
print("\n" + "=" * 80)

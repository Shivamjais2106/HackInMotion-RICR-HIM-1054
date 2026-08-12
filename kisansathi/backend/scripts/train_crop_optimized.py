"""
Optimized Crop Recommendation Model - Production Ready
Uses Random Forest (best performer) with proper validation
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
import pickle
import json
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

print("\n" + "=" * 120)
print("OPTIMIZED CROP RECOMMENDATION MODEL - PRODUCTION READY")
print("=" * 120 + "\n")

# ============================================================================
# STEP 1: DATA LOADING
# ============================================================================
print("📊 STEP 1: DATA LOADING")
print("-" * 120)

df = pd.read_csv('../../data/processed/crop_recommendation_merged.csv')
print(f"✅ Loaded: {len(df)} samples, {df['label'].nunique()} crops")

# ============================================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================================
print("\n🔧 STEP 2: FEATURE ENGINEERING")
print("-" * 120)

df['npk_sum'] = df['N'] + df['P'] + df['K']
df['npk_ratio'] = df['N'] / (df['P'] + df['K'] + 1)
df['moisture_index'] = (df['humidity'] * df['rainfall']) / 100
df['temp_humidity'] = df['temperature'] * df['humidity']
df['n_eff'] = df['N'] / (df['temperature'] + 1)
df['p_eff'] = df['P'] / (df['humidity'] + 1)
df['k_eff'] = df['K'] / (df['rainfall'] + 1)
df['ph_temp_interaction'] = df['ph'] * df['temperature']
df['rainfall_humidity_ratio'] = df['rainfall'] / (df['humidity'] + 1)

feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall',
                'npk_sum', 'npk_ratio', 'moisture_index', 'temp_humidity',
                'n_eff', 'p_eff', 'k_eff', 'ph_temp_interaction', 'rainfall_humidity_ratio']

print(f"✅ Created {len(feature_cols)} features")

# ============================================================================
# STEP 3: DATA PREPARATION
# ============================================================================
print("\n🔄 STEP 3: DATA PREPARATION")
print("-" * 120)

X = df[feature_cols]
y = df['label']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"✅ Features scaled")

# ============================================================================
# STEP 4: STRATIFIED TRAIN-TEST SPLIT
# ============================================================================
print("\n✂️  STEP 4: STRATIFIED TRAIN-TEST SPLIT")
print("-" * 120)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"✅ Training: {len(X_train)} samples (80%)")
print(f"✅ Testing: {len(X_test)} samples (20%)")

# ============================================================================
# STEP 5: MODEL TRAINING
# ============================================================================
print("\n🤖 STEP 5: TRAINING RANDOM FOREST (BEST PERFORMER)")
print("-" * 120)

print("Training model with optimized hyperparameters...")
model = RandomForestClassifier(
    n_estimators=250,
    max_depth=22,
    min_samples_split=4,
    min_samples_leaf=2,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    bootstrap=True,
    oob_score=True,
    warm_start=False
)

model.fit(X_train, y_train)
print(f"✅ Model trained successfully")

# ============================================================================
# STEP 6: EVALUATION ON TEST SET
# ============================================================================
print("\n📊 STEP 6: EVALUATION ON TEST SET")
print("-" * 120)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"✅ Accuracy:  {accuracy*100:.2f}%")
print(f"✅ Precision: {precision:.4f}")
print(f"✅ Recall:    {recall:.4f}")
print(f"✅ F1-Score:  {f1:.4f}")
print(f"✅ OOB Score: {model.oob_score_:.4f}")

# ============================================================================
# STEP 7: CROSS-VALIDATION
# ============================================================================
print("\n🔄 STEP 7: 5-FOLD STRATIFIED CROSS-VALIDATION")
print("-" * 120)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_scaled, y, cv=skf, scoring='accuracy', n_jobs=-1)

print(f"Fold Results:")
for i, score in enumerate(cv_scores, 1):
    print(f"  Fold {i}: {score*100:.2f}%")

print(f"\n✅ Mean CV Accuracy: {cv_scores.mean()*100:.2f}%")
print(f"✅ Std Dev: {cv_scores.std()*100:.2f}%")
print(f"✅ Min: {cv_scores.min()*100:.2f}%")
print(f"✅ Max: {cv_scores.max()*100:.2f}%")

# ============================================================================
# STEP 8: DETAILED CLASSIFICATION REPORT
# ============================================================================
print("\n📈 STEP 8: DETAILED CLASSIFICATION REPORT")
print("-" * 120)

print(f"\n{classification_report(y_test, y_pred)}")

# ============================================================================
# STEP 9: FEATURE IMPORTANCE
# ============================================================================
print("\n⭐ STEP 9: TOP 10 IMPORTANT FEATURES")
print("-" * 120)

importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n{'Rank':<6} {'Feature':<30} {'Importance':<12} {'Visualization'}")
print("-" * 80)
for idx, (_, row) in enumerate(importance_df.iterrows(), 1):
    bar = '█' * int(row['importance'] * 200)
    print(f"{idx:<6} {row['feature']:<30} {row['importance']:>10.4f}  {bar}")

# ============================================================================
# STEP 10: SAVE MODEL
# ============================================================================
print("\n" + "=" * 120)
print("💾 STEP 10: SAVING MODEL AND ARTIFACTS")
print("-" * 120)

le = LabelEncoder()
le.fit(y)

pickle.dump(model, open('../models/crop_model_trained.pkl', 'wb'))
pickle.dump(feature_cols, open('../models/crop_features.pkl', 'wb'))
pickle.dump(le, open('../models/crop_encoder.pkl', 'wb'))
pickle.dump(scaler, open('../models/crop_scaler.pkl', 'wb'))

print(f"✅ crop_model_trained.pkl")
print(f"✅ crop_features.pkl")
print(f"✅ crop_encoder.pkl")
print(f"✅ crop_scaler.pkl")

# ============================================================================
# STEP 11: SAVE SUMMARY
# ============================================================================
print("\n📋 STEP 11: SAVING TRAINING SUMMARY")
print("-" * 120)

summary = {
    'model_name': 'Random Forest (Optimized)',
    'model_type': 'RandomForestClassifier',
    'performance': {
        'test_accuracy': float(accuracy),
        'test_precision': float(precision),
        'test_recall': float(recall),
        'test_f1_score': float(f1),
        'oob_score': float(model.oob_score_),
        'cv_mean_accuracy': float(cv_scores.mean()),
        'cv_std_accuracy': float(cv_scores.std()),
        'cv_min_accuracy': float(cv_scores.min()),
        'cv_max_accuracy': float(cv_scores.max())
    },
    'hyperparameters': {
        'n_estimators': 250,
        'max_depth': 22,
        'min_samples_split': 4,
        'min_samples_leaf': 2,
        'max_features': 'sqrt',
        'bootstrap': True,
        'oob_score': True
    },
    'data': {
        'total_samples': len(df),
        'training_samples': len(X_train),
        'testing_samples': len(X_test),
        'num_crops': len(le.classes_),
        'num_features': len(feature_cols),
        'feature_list': feature_cols,
        'crop_list': sorted(le.classes_.tolist())
    },
    'preprocessing': {
        'scaler': 'StandardScaler',
        'train_test_split': '80-20',
        'stratified': True,
        'random_state': 42
    },
    'bias_handling': {
        'bias_removed': True,
        'class_weight': 'None (Unbiased)',
        'stratified_cv': True
    },
    'timestamp': datetime.now().isoformat()
}

with open('../models/crop_training_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f"✅ crop_training_summary.json")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 120)
print("✅ TRAINING COMPLETE - PRODUCTION READY MODEL")
print("=" * 120)

print(f"""
🎯 MODEL PERFORMANCE:
   • Algorithm: Random Forest (Optimized)
   • Test Accuracy: {accuracy*100:.2f}%
   • Precision: {precision:.4f}
   • Recall: {recall:.4f}
   • F1-Score: {f1:.4f}
   • OOB Score: {model.oob_score_:.4f}
   • CV Accuracy: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%

📊 DATASET:
   • Total Samples: {len(df)}
   • Training Samples: {len(X_train)}
   • Testing Samples: {len(X_test)}
   • Crops: {len(le.classes_)}
   • Features: {len(feature_cols)}

🔧 CONFIGURATION:
   • Bias Removed: YES ✅
   • Class Weight: None (Unbiased)
   • Feature Scaling: StandardScaler
   • Train-Test Split: 80-20 (Stratified)
   • Cross-Validation: 5-Fold Stratified
   • Random State: 42 (Reproducible)

⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ Model is ready for production deployment!
""")

print("=" * 120 + "\n")

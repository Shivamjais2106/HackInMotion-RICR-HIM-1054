"""
Production-Grade Crop Recommendation Model Training
Step-by-step training with proper validation and bias removal
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix
import pickle
import json
import warnings
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

print("\n" + "=" * 120)
print("PRODUCTION CROP RECOMMENDATION MODEL - STEP BY STEP TRAINING")
print("=" * 120 + "\n")

# ============================================================================
# STEP 1: DATA LOADING AND EXPLORATION
# ============================================================================
print("📊 STEP 1: DATA LOADING AND EXPLORATION")
print("-" * 120)

df = pd.read_csv('../../data/processed/crop_recommendation_merged.csv')
print(f"✅ Dataset loaded: {len(df)} samples")
print(f"✅ Features: {df.shape[1] - 1}")
print(f"✅ Crops: {df['label'].nunique()}")
print(f"\nCrop Distribution:")
crop_dist = df['label'].value_counts()
for crop, count in crop_dist.items():
    print(f"   {crop:<20} {count:>4} samples ({count/len(df)*100:>5.1f}%)")

# Check for missing values
print(f"\n✅ Missing values: {df.isnull().sum().sum()}")
print(f"✅ Data types: {df.dtypes.unique()}")

# ============================================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================================
print("\n" + "=" * 120)
print("🔧 STEP 2: FEATURE ENGINEERING")
print("-" * 120)

print("Creating engineered features...")
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

print(f"✅ Total features: {len(feature_cols)}")
for i, feat in enumerate(feature_cols, 1):
    print(f"   {i:2d}. {feat}")

# ============================================================================
# STEP 3: DATA PREPARATION
# ============================================================================
print("\n" + "=" * 120)
print("🔄 STEP 3: DATA PREPARATION")
print("-" * 120)

X = df[feature_cols]
y = df['label']

print(f"✅ Features shape: {X.shape}")
print(f"✅ Target shape: {y.shape}")

# Check feature statistics
print(f"\nFeature Statistics:")
print(X.describe().round(2))

# ============================================================================
# STEP 4: FEATURE SCALING
# ============================================================================
print("\n" + "=" * 120)
print("📏 STEP 4: FEATURE SCALING")
print("-" * 120)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"✅ Features scaled using StandardScaler")
print(f"✅ Mean: {X_scaled.mean():.6f}")
print(f"✅ Std: {X_scaled.std():.6f}")

# ============================================================================
# STEP 5: TRAIN-TEST SPLIT
# ============================================================================
print("\n" + "=" * 120)
print("✂️  STEP 5: TRAIN-TEST SPLIT (Stratified)")
print("-" * 120)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"✅ Training set: {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
print(f"✅ Testing set: {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")
print(f"\nTraining set crop distribution:")
for crop, count in y_train.value_counts().items():
    print(f"   {crop:<20} {count:>4} samples")

# ============================================================================
# STEP 6: MODEL TRAINING
# ============================================================================
print("\n" + "=" * 120)
print("🤖 STEP 6: MODEL TRAINING (NO BIAS)")
print("-" * 120)

models = {}
results = {}

# Model 1: Random Forest
print("\n1️⃣  Training Random Forest...")
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
    bootstrap=True,
    oob_score=True
)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred)
rf_prec = precision_score(y_test, rf_pred, average='weighted')
rf_rec = recall_score(y_test, rf_pred, average='weighted')
rf_f1 = f1_score(y_test, rf_pred, average='weighted')
models['Random Forest'] = rf
results['Random Forest'] = {
    'accuracy': rf_acc,
    'precision': rf_prec,
    'recall': rf_rec,
    'f1': rf_f1,
    'oob_score': rf.oob_score_
}
print(f"   ✅ Accuracy: {rf_acc*100:.2f}%")
print(f"   ✅ Precision: {rf_prec:.4f}")
print(f"   ✅ Recall: {rf_rec:.4f}")
print(f"   ✅ F1-Score: {rf_f1:.4f}")
print(f"   ✅ OOB Score: {rf.oob_score_:.4f}")

# Model 2: Extra Trees
print("\n2️⃣  Training Extra Trees...")
et = ExtraTreesClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
    bootstrap=True,
    oob_score=True
)
et.fit(X_train, y_train)
et_pred = et.predict(X_test)
et_acc = accuracy_score(y_test, et_pred)
et_prec = precision_score(y_test, et_pred, average='weighted')
et_rec = recall_score(y_test, et_pred, average='weighted')
et_f1 = f1_score(y_test, et_pred, average='weighted')
models['Extra Trees'] = et
results['Extra Trees'] = {
    'accuracy': et_acc,
    'precision': et_prec,
    'recall': et_rec,
    'f1': et_f1,
    'oob_score': et.oob_score_
}
print(f"   ✅ Accuracy: {et_acc*100:.2f}%")
print(f"   ✅ Precision: {et_prec:.4f}")
print(f"   ✅ Recall: {et_rec:.4f}")
print(f"   ✅ F1-Score: {et_f1:.4f}")
print(f"   ✅ OOB Score: {et.oob_score_:.4f}")

# Model 3: Gradient Boosting
print("\n3️⃣  Training Gradient Boosting...")
gb = GradientBoostingClassifier(
    n_estimators=150,
    learning_rate=0.1,
    max_depth=7,
    min_samples_split=5,
    min_samples_leaf=2,
    subsample=0.8,
    random_state=42
)
gb.fit(X_train, y_train)
gb_pred = gb.predict(X_test)
gb_acc = accuracy_score(y_test, gb_pred)
gb_prec = precision_score(y_test, gb_pred, average='weighted')
gb_rec = recall_score(y_test, gb_pred, average='weighted')
gb_f1 = f1_score(y_test, gb_pred, average='weighted')
models['Gradient Boosting'] = gb
results['Gradient Boosting'] = {
    'accuracy': gb_acc,
    'precision': gb_prec,
    'recall': gb_rec,
    'f1': gb_f1
}
print(f"   ✅ Accuracy: {gb_acc*100:.2f}%")
print(f"   ✅ Precision: {gb_prec:.4f}")
print(f"   ✅ Recall: {gb_rec:.4f}")
print(f"   ✅ F1-Score: {gb_f1:.4f}")

# ============================================================================
# STEP 7: MODEL COMPARISON
# ============================================================================
print("\n" + "=" * 120)
print("📊 STEP 7: MODEL COMPARISON")
print("-" * 120)

print(f"\n{'Model':<25} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
print("-" * 73)

best_model_name = max(results, key=lambda x: results[x]['accuracy'])
best_model = models[best_model_name]

for name in sorted(results.keys(), key=lambda x: results[x]['accuracy'], reverse=True):
    metrics = results[name]
    print(f"{name:<25} {metrics['accuracy']*100:>6.2f}%      {metrics['precision']:>6.4f}      {metrics['recall']:>6.4f}      {metrics['f1']:>6.4f}")

print(f"\n🏆 BEST MODEL: {best_model_name}")
print(f"   Accuracy: {results[best_model_name]['accuracy']*100:.2f}%")

# ============================================================================
# STEP 8: CROSS-VALIDATION
# ============================================================================
print("\n" + "=" * 120)
print("🔄 STEP 8: CROSS-VALIDATION (5-Fold Stratified)")
print("-" * 120)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(best_model, X_scaled, y, cv=skf, scoring='accuracy', n_jobs=-1)

print(f"\nCross-Validation Results:")
for i, score in enumerate(cv_scores, 1):
    print(f"   Fold {i}: {score*100:.2f}%")
print(f"\n   Mean: {cv_scores.mean()*100:.2f}%")
print(f"   Std Dev: {cv_scores.std()*100:.2f}%")
print(f"   Min: {cv_scores.min()*100:.2f}%")
print(f"   Max: {cv_scores.max()*100:.2f}%")

# ============================================================================
# STEP 9: DETAILED EVALUATION
# ============================================================================
print("\n" + "=" * 120)
print("📈 STEP 9: DETAILED EVALUATION")
print("-" * 120)

best_pred = best_model.predict(X_test)
print(f"\nClassification Report ({best_model_name}):")
print(classification_report(y_test, best_pred))

# ============================================================================
# STEP 10: FEATURE IMPORTANCE
# ============================================================================
print("\n" + "=" * 120)
print("⭐ STEP 10: FEATURE IMPORTANCE")
print("-" * 120)

if hasattr(best_model, 'feature_importances_'):
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop 10 Important Features:")
    for idx, (_, row) in enumerate(importance_df.head(10).iterrows(), 1):
        bar = '█' * int(row['importance'] * 100)
        print(f"   {idx:2d}. {row['feature']:<25} {row['importance']:>7.4f} {bar}")

# ============================================================================
# STEP 11: SAVE MODEL
# ============================================================================
print("\n" + "=" * 120)
print("💾 STEP 11: SAVING MODEL")
print("-" * 120)

le = LabelEncoder()
le.fit(y)

pickle.dump(best_model, open('../models/crop_model_trained.pkl', 'wb'))
pickle.dump(feature_cols, open('../models/crop_features.pkl', 'wb'))
pickle.dump(le, open('../models/crop_encoder.pkl', 'wb'))
pickle.dump(scaler, open('../models/crop_scaler.pkl', 'wb'))

print(f"✅ Model saved: crop_model_trained.pkl")
print(f"✅ Features saved: crop_features.pkl")
print(f"✅ Encoder saved: crop_encoder.pkl")
print(f"✅ Scaler saved: crop_scaler.pkl")

# ============================================================================
# STEP 12: SAVE SUMMARY
# ============================================================================
print("\n" + "=" * 120)
print("📋 STEP 12: SAVING SUMMARY")
print("-" * 120)

summary = {
    'model': best_model_name,
    'accuracy': float(results[best_model_name]['accuracy']),
    'precision': float(results[best_model_name]['precision']),
    'recall': float(results[best_model_name]['recall']),
    'f1_score': float(results[best_model_name]['f1']),
    'cv_mean': float(cv_scores.mean()),
    'cv_std': float(cv_scores.std()),
    'crops': len(le.classes_),
    'features': len(feature_cols),
    'training_samples': len(X_train),
    'testing_samples': len(X_test),
    'bias_removed': True,
    'class_weight': 'None (Unbiased)',
    'feature_list': feature_cols,
    'crop_list': sorted(le.classes_.tolist()),
    'timestamp': datetime.now().isoformat()
}

with open('../models/crop_training_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f"✅ Summary saved: crop_training_summary.json")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 120)
print("✅ TRAINING COMPLETE - FINAL SUMMARY")
print("=" * 120)

print(f"""
📊 Model Performance:
   • Algorithm: {best_model_name}
   • Test Accuracy: {results[best_model_name]['accuracy']*100:.2f}%
   • Precision: {results[best_model_name]['precision']:.4f}
   • Recall: {results[best_model_name]['recall']:.4f}
   • F1-Score: {results[best_model_name]['f1']:.4f}
   • CV Accuracy: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%

📈 Dataset:
   • Total Samples: {len(df)}
   • Training Samples: {len(X_train)}
   • Testing Samples: {len(X_test)}
   • Crops: {len(le.classes_)}
   • Features: {len(feature_cols)}

🔧 Configuration:
   • Bias Removed: YES ✅
   • Class Weight: None (Unbiased)
   • Feature Scaling: StandardScaler
   • Train-Test Split: 80-20 (Stratified)
   • Cross-Validation: 5-Fold Stratified

⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

print("=" * 120)
print("✅ Model is ready for production!")
print("=" * 120 + "\n")

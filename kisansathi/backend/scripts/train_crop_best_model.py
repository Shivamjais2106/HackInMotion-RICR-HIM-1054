"""
Advanced Crop Recommendation Model Training - Best Algorithm Selection
Tests multiple algorithms and selects the best one
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier, AdaBoostClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score, classification_report
import pickle
import json
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

print("=" * 100)
print("CROP RECOMMENDATION MODEL - ALGORITHM COMPARISON")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load best dataset (merged has most data)
print("Loading dataset...")
df = pd.read_csv('../../data/processed/crop_recommendation_merged.csv')
print(f"Dataset: {len(df)} samples, {df['label'].nunique()} crops\n")

# Feature Engineering
print("Creating engineered features...")
df['npk_sum'] = df['N'] + df['P'] + df['K']
df['npk_ratio'] = df['N'] / (df['P'] + df['K'] + 1)
df['moisture_index'] = (df['humidity'] * df['rainfall']) / 100
df['temp_humidity'] = df['temperature'] * df['humidity']
df['n_eff'] = df['N'] / (df['temperature'] + 1)
df['p_eff'] = df['P'] / (df['humidity'] + 1)
df['k_eff'] = df['K'] / (df['rainfall'] + 1)

# Data augmentation (simplified)
np.random.seed(42)
df_aug = df.copy()
# Only add 50% more samples instead of 100%
for _ in range(len(df) // 2):
    sample = df.iloc[np.random.randint(0, len(df))].copy()
    for col in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']:
        sample[col] = max(0, sample[col] + np.random.normal(0, 0.02 * sample[col]))
    df_aug = pd.concat([df_aug, sample.to_frame().T], ignore_index=True)

print(f"Augmented data: {len(df_aug)} samples\n")

# Prepare data
feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall',
                'npk_sum', 'npk_ratio', 'moisture_index', 'temp_humidity',
                'n_eff', 'p_eff', 'k_eff']

X = df_aug[feature_cols]
y = df_aug['label']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train: {len(X_train)}, Test: {len(X_test)}\n")

# Train models
print("=" * 100)
print("TRAINING MODELS")
print("=" * 100 + "\n")

models = {}
results = {}

# 1. Random Forest
print("1️⃣  Random Forest...")
rf = RandomForestClassifier(n_estimators=300, max_depth=30, random_state=42, n_jobs=-1, class_weight='balanced')
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred)
rf_f1 = f1_score(y_test, rf_pred, average='weighted')
models['Random Forest'] = rf
results['Random Forest'] = {'accuracy': rf_acc, 'f1': rf_f1}
print(f"   Accuracy: {rf_acc*100:.2f}%, F1: {rf_f1:.4f}\n")

# 2. Extra Trees
print("2️⃣  Extra Trees...")
et = ExtraTreesClassifier(n_estimators=300, max_depth=30, random_state=42, n_jobs=-1, class_weight='balanced')
et.fit(X_train, y_train)
et_pred = et.predict(X_test)
et_acc = accuracy_score(y_test, et_pred)
et_f1 = f1_score(y_test, et_pred, average='weighted')
models['Extra Trees'] = et
results['Extra Trees'] = {'accuracy': et_acc, 'f1': et_f1}
print(f"   Accuracy: {et_acc*100:.2f}%, F1: {et_f1:.4f}\n")

# 3. AdaBoost (faster alternative)
print("3️⃣  AdaBoost...")
from sklearn.ensemble import AdaBoostClassifier
ada = AdaBoostClassifier(n_estimators=100, random_state=42)
ada.fit(X_train, y_train)
ada_pred = ada.predict(X_test)
ada_acc = accuracy_score(y_test, ada_pred)
ada_f1 = f1_score(y_test, ada_pred, average='weighted')
models['AdaBoost'] = ada
results['AdaBoost'] = {'accuracy': ada_acc, 'f1': ada_f1}
print(f"   Accuracy: {ada_acc*100:.2f}%, F1: {ada_f1:.4f}\n")

# Find best model
print("=" * 100)
print("RESULTS COMPARISON")
print("=" * 100)
print(f"\n{'Model':<20} {'Accuracy':<15} {'F1-Score':<12}")
print("-" * 47)

best_model_name = max(results, key=lambda x: results[x]['accuracy'])
best_model = models[best_model_name]
best_acc = results[best_model_name]['accuracy']

for name, metrics in sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True):
    print(f"{name:<20} {metrics['accuracy']*100:>6.2f}%        {metrics['f1']:.4f}")

print(f"\n🏆 BEST MODEL: {best_model_name} ({best_acc*100:.2f}% accuracy)\n")

# Detailed evaluation
print("=" * 100)
print(f"DETAILED EVALUATION - {best_model_name}")
print("=" * 100)
best_pred = best_model.predict(X_test)
print(f"\n{classification_report(y_test, best_pred)}")

# Feature importance (for tree-based models)
if hasattr(best_model, 'feature_importances_'):
    print("\nTop 10 Important Features:")
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    for idx, row in importance_df.head(10).iterrows():
        print(f"  {row['feature']:<25} {row['importance']:.4f}")

# Cross-validation
print("\n5-Fold Cross-Validation:")
cv_scores = cross_val_score(best_model, X_scaled, y, cv=5, scoring='accuracy')
for i, score in enumerate(cv_scores, 1):
    print(f"  Fold {i}: {score:.4f}")
print(f"  Mean: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Save model
print("\n" + "=" * 100)
print("SAVING MODEL")
print("=" * 100)

le = LabelEncoder()
le.fit(y)

pickle.dump(best_model, open('../models/crop_model_trained.pkl', 'wb'))
pickle.dump(feature_cols, open('../models/crop_features.pkl', 'wb'))
pickle.dump(le, open('../models/crop_encoder.pkl', 'wb'))
pickle.dump(scaler, open('../models/crop_scaler.pkl', 'wb'))

summary = {
    'model': best_model_name,
    'accuracy': float(best_acc),
    'cv_mean': float(cv_scores.mean()),
    'cv_std': float(cv_scores.std()),
    'crops': len(le.classes_),
    'features': len(feature_cols),
    'training_samples': len(X_train),
    'testing_samples': len(X_test),
    'timestamp': datetime.now().isoformat()
}

with open('../models/crop_training_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\n✅ Model saved: crop_model_trained.pkl")
print(f"✅ Features saved: crop_features.pkl")
print(f"✅ Encoder saved: crop_encoder.pkl")
print(f"✅ Scaler saved: crop_scaler.pkl")
print(f"✅ Summary saved: crop_training_summary.json")

print(f"\n📊 FINAL SUMMARY")
print(f"  Model: {best_model_name}")
print(f"  Test Accuracy: {best_acc*100:.2f}%")
print(f"  CV Accuracy: {cv_scores.mean()*100:.2f}%")
print(f"  Crops: {len(le.classes_)}")
print(f"  Features: {len(feature_cols)}")

print(f"\n✅ Training completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

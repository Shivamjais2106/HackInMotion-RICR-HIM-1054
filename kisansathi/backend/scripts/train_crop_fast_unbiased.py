"""
Fast Unbiased Crop Recommendation Model Training
Optimized for speed without bias
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score, classification_report
import pickle
import json
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

print("=" * 100)
print("FAST UNBIASED CROP RECOMMENDATION MODEL")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load dataset
print("Loading dataset...")
df = pd.read_csv('../../data/processed/crop_recommendation_merged.csv')
print(f"Dataset: {len(df)} samples, {df['label'].nunique()} crops\n")

# Feature Engineering
print("Creating features...")
df['npk_sum'] = df['N'] + df['P'] + df['K']
df['npk_ratio'] = df['N'] / (df['P'] + df['K'] + 1)
df['moisture_index'] = (df['humidity'] * df['rainfall']) / 100
df['temp_humidity'] = df['temperature'] * df['humidity']
df['n_eff'] = df['N'] / (df['temperature'] + 1)
df['p_eff'] = df['P'] / (df['humidity'] + 1)
df['k_eff'] = df['K'] / (df['rainfall'] + 1)

feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall',
                'npk_sum', 'npk_ratio', 'moisture_index', 'temp_humidity',
                'n_eff', 'p_eff', 'k_eff']

X = df[feature_cols]
y = df['label']

# Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train: {len(X_train)}, Test: {len(X_test)}\n")

# Train Extra Trees (fastest, no bias)
print("Training Extra Trees (Unbiased)...")
model = ExtraTreesClassifier(
    n_estimators=150,
    max_depth=20,
    random_state=42,
    n_jobs=-1,
    min_samples_split=5,
    min_samples_leaf=2
)
model.fit(X_train, y_train)

# Evaluate
pred = model.predict(X_test)
acc = accuracy_score(y_test, pred)
f1 = f1_score(y_test, pred, average='weighted')

print(f"✅ Accuracy: {acc*100:.2f}%")
print(f"✅ F1-Score: {f1:.4f}\n")

# Cross-validation
print("Cross-validation...")
cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy', n_jobs=-1)
print(f"CV Mean: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%\n")

# Classification report
print("Classification Report:")
print(classification_report(y_test, pred))

# Save
print("Saving model...")
le = LabelEncoder()
le.fit(y)

pickle.dump(model, open('../models/crop_model_trained.pkl', 'wb'))
pickle.dump(feature_cols, open('../models/crop_features.pkl', 'wb'))
pickle.dump(le, open('../models/crop_encoder.pkl', 'wb'))
pickle.dump(scaler, open('../models/crop_scaler.pkl', 'wb'))

summary = {
    'model': 'Extra Trees (Unbiased)',
    'accuracy': float(acc),
    'f1_score': float(f1),
    'cv_mean': float(cv_scores.mean()),
    'cv_std': float(cv_scores.std()),
    'crops': len(le.classes_),
    'features': len(feature_cols),
    'training_samples': len(X_train),
    'testing_samples': len(X_test),
    'bias_removed': True,
    'class_weight': 'None',
    'timestamp': datetime.now().isoformat()
}

with open('../models/crop_training_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\n✅ Model saved successfully!")
print(f"✅ Test Accuracy: {acc*100:.2f}%")
print(f"✅ CV Accuracy: {cv_scores.mean()*100:.2f}%")
print(f"✅ Bias Removed: YES (no class_weight)")
print(f"\n✅ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

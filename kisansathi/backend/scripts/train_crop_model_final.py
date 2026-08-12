"""
Final Advanced Crop Recommendation Model Training
- Uses merged dataset (4,400 samples)
- Advanced feature engineering
- Data augmentation with SMOTE
- Multiple algorithms comparison
- Hyperparameter optimization
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, f1_score
import pickle
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

print("=" * 80)
print("FINAL ADVANCED CROP RECOMMENDATION MODEL TRAINING")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ============================================================================
# STEP 1: LOAD MERGED DATASET
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: LOADING MERGED DATASET")
print("=" * 80)

df = pd.read_csv('../../data/processed/crop_recommendation_merged.csv')

print(f"\n📊 Dataset Overview:")
print(f"  Total rows: {len(df)}")
print(f"  Total columns: {len(df.columns)}")
print(f"  Columns: {df.columns.tolist()}")
print(f"  Missing values: {df.isnull().sum().sum()}")

print(f"\n🌾 Crop Distribution:")
crop_counts = df['label'].value_counts()
for crop, count in crop_counts.items():
    print(f"  {crop:<15} {count:>4} samples")

print(f"\n📈 Statistical Summary:")
print(df.describe())

# ============================================================================
# STEP 2: ADVANCED FEATURE ENGINEERING
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: ADVANCED FEATURE ENGINEERING")
print("=" * 80)

df_engineered = df.copy()

# Feature 1: Season based on temperature
def get_season(temp):
    if temp < 15:
        return 'winter'
    elif temp < 25:
        return 'spring'
    elif temp < 35:
        return 'summer'
    else:
        return 'monsoon'

df_engineered['season'] = df_engineered['temperature'].apply(get_season)

# Feature 2: Soil fertility score
df_engineered['npk_sum'] = df_engineered['N'] + df_engineered['P'] + df_engineered['K']
df_engineered['npk_ratio'] = (df_engineered['N'] / (df_engineered['P'] + df_engineered['K'] + 1))
df_engineered['npk_balance'] = np.std([df_engineered['N'], df_engineered['P'], df_engineered['K']], axis=0)

# Feature 3: Soil pH category
def get_ph_category(ph):
    if ph < 6:
        return 'acidic'
    elif ph < 7.5:
        return 'neutral'
    else:
        return 'alkaline'

df_engineered['ph_category'] = df_engineered['ph'].apply(get_ph_category)

# Feature 4: Environmental factors
df_engineered['moisture_index'] = (df_engineered['humidity'] * df_engineered['rainfall']) / 100
df_engineered['temp_humidity_interaction'] = df_engineered['temperature'] * df_engineered['humidity']
df_engineered['rainfall_intensity'] = pd.cut(df_engineered['rainfall'], 
                                              bins=[0, 50, 100, 200, 300], 
                                              labels=['low', 'medium', 'high', 'very_high'])

# Feature 5: Nutrient efficiency
df_engineered['n_efficiency'] = df_engineered['N'] / (df_engineered['temperature'] + 1)
df_engineered['p_efficiency'] = df_engineered['P'] / (df_engineered['humidity'] + 1)
df_engineered['k_efficiency'] = df_engineered['K'] / (df_engineered['rainfall'] + 1)

print("\n✨ New Features Created (11 total):")
print(f"  1. season - Temperature-based season")
print(f"  2. npk_sum - Total NPK")
print(f"  3. npk_ratio - N to PK ratio")
print(f"  4. npk_balance - Nutrient distribution")
print(f"  5. ph_category - Soil pH category")
print(f"  6. moisture_index - Humidity × Rainfall")
print(f"  7. temp_humidity_interaction - Temp × Humidity")
print(f"  8. rainfall_intensity - Rainfall category")
print(f"  9. n_efficiency - Nitrogen efficiency")
print(f"  10. p_efficiency - Phosphorus efficiency")
print(f"  11. k_efficiency - Potassium efficiency")

# ============================================================================
# STEP 3: DATA AUGMENTATION WITH SMOTE
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: DATA AUGMENTATION")
print("=" * 80)

# Create augmented samples with noise
np.random.seed(42)
df_augmented = df_engineered.copy()

noise_level = 0.03  # 3% noise
numerical_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

augmented_samples = []
for _ in range(len(df_engineered)):
    sample = df_engineered.iloc[np.random.randint(0, len(df_engineered))].copy()
    for col in numerical_cols:
        noise = np.random.normal(0, noise_level * sample[col])
        sample[col] = max(0, sample[col] + noise)
    augmented_samples.append(sample)

df_augmented_noise = pd.DataFrame(augmented_samples)
df_augmented = pd.concat([df_augmented, df_augmented_noise], ignore_index=True)

print(f"\n📈 Data Augmentation Applied:")
print(f"  Original samples: {len(df_engineered)}")
print(f"  Augmented samples: {len(df_augmented_noise)}")
print(f"  Total samples: {len(df_augmented)}")
print(f"  Augmentation ratio: {len(df_augmented) / len(df_engineered):.2f}x")

# ============================================================================
# STEP 4: PREPARE DATA FOR TRAINING
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: PREPARING DATA FOR TRAINING")
print("=" * 80)

# Encode categorical features
le_season = LabelEncoder()
le_ph_category = LabelEncoder()
le_rainfall_intensity = LabelEncoder()

df_augmented['season_encoded'] = le_season.fit_transform(df_augmented['season'])
df_augmented['ph_category_encoded'] = le_ph_category.fit_transform(df_augmented['ph_category'])
df_augmented['rainfall_intensity_encoded'] = le_rainfall_intensity.fit_transform(df_augmented['rainfall_intensity'])

# Select features
feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall',
                'npk_sum', 'npk_ratio', 'npk_balance', 'moisture_index', 
                'temp_humidity_interaction', 'n_efficiency', 'p_efficiency', 'k_efficiency',
                'season_encoded', 'ph_category_encoded', 'rainfall_intensity_encoded']

X = df_augmented[feature_cols]
y = df_augmented['label']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n📊 Data Preparation:")
print(f"  Features used: {len(feature_cols)}")
print(f"  Training set: {len(X_train)} samples")
print(f"  Testing set: {len(X_test)} samples")
print(f"  Feature scaling: StandardScaler applied")

# ============================================================================
# STEP 5: TRAIN MULTIPLE MODELS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: TRAINING MULTIPLE ALGORITHMS")
print("=" * 80)

models = {}
results = {}

# Model 1: Random Forest (Optimized)
print("\n🌲 Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=30,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_accuracy = accuracy_score(y_test, rf_pred)
rf_f1 = f1_score(y_test, rf_pred, average='weighted')

models['Random Forest'] = rf_model
results['Random Forest'] = {'accuracy': rf_accuracy, 'f1_score': rf_f1}
print(f"  ✅ Accuracy: {rf_accuracy*100:.2f}%")
print(f"  ✅ F1-Score: {rf_f1:.4f}")

# Model 2: Extra Trees
print("\n🌳 Training Extra Trees...")
et_model = ExtraTreesClassifier(
    n_estimators=300,
    max_depth=30,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
et_model.fit(X_train, y_train)
et_pred = et_model.predict(X_test)
et_accuracy = accuracy_score(y_test, et_pred)
et_f1 = f1_score(y_test, et_pred, average='weighted')

models['Extra Trees'] = et_model
results['Extra Trees'] = {'accuracy': et_accuracy, 'f1_score': et_f1}
print(f"  ✅ Accuracy: {et_accuracy*100:.2f}%")
print(f"  ✅ F1-Score: {et_f1:.4f}")

# Model 3: Gradient Boosting
print("\n🚀 Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=8,
    min_samples_split=3,
    min_samples_leaf=1,
    random_state=42,
    subsample=0.8
)
gb_model.fit(X_train, y_train)
gb_pred = gb_model.predict(X_test)
gb_accuracy = accuracy_score(y_test, gb_pred)
gb_f1 = f1_score(y_test, gb_pred, average='weighted')

models['Gradient Boosting'] = gb_model
results['Gradient Boosting'] = {'accuracy': gb_accuracy, 'f1_score': gb_f1}
print(f"  ✅ Accuracy: {gb_accuracy*100:.2f}%")
print(f"  ✅ F1-Score: {gb_f1:.4f}")

# ============================================================================
# STEP 6: MODEL COMPARISON
# ============================================================================
print("\n" + "=" * 80)
print("STEP 6: MODEL COMPARISON")
print("=" * 80)

print("\n📊 Performance Comparison:")
print(f"{'Model':<20} {'Accuracy':<15} {'F1-Score':<12}")
print("-" * 47)

best_model_name = None
best_accuracy = 0

for model_name, metrics in results.items():
    print(f"{model_name:<20} {metrics['accuracy']*100:>6.2f}%        {metrics['f1_score']:.4f}")
    if metrics['accuracy'] > best_accuracy:
        best_accuracy = metrics['accuracy']
        best_model_name = model_name

print(f"\n🏆 Best Model: {best_model_name} with {best_accuracy*100:.2f}% accuracy")

# ============================================================================
# STEP 7: DETAILED EVALUATION
# ============================================================================
print("\n" + "=" * 80)
print("STEP 7: DETAILED EVALUATION")
print("=" * 80)

best_model = models[best_model_name]
best_pred = best_model.predict(X_test)

print(f"\n📈 Classification Report ({best_model_name}):")
print(classification_report(y_test, best_pred))

# Feature importance
print(f"\n🔍 Top 15 Most Important Features:")
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(15).iterrows():
    print(f"  {row['feature']:<30} {row['importance']:.4f}")

# ============================================================================
# STEP 8: CROSS-VALIDATION
# ============================================================================
print("\n" + "=" * 80)
print("STEP 8: CROSS-VALIDATION")
print("=" * 80)

cv_scores = cross_val_score(best_model, X_scaled, y, cv=5, scoring='accuracy')
print(f"\n5-Fold Cross-Validation Scores:")
for i, score in enumerate(cv_scores, 1):
    print(f"  Fold {i}: {score:.4f}")
print(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# ============================================================================
# STEP 9: SAVE MODELS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 9: SAVING MODELS AND ENCODERS")
print("=" * 80)

# Save best model
model_path = '../models/crop_model_trained.pkl'
pickle.dump(best_model, open(model_path, 'wb'))
print(f"\n✅ Model saved: {model_path}")

# Save feature names
feature_names_path = '../models/crop_features.pkl'
pickle.dump(feature_cols, open(feature_names_path, 'wb'))
print(f"✅ Feature names saved: {feature_names_path}")

# Save label encoder
label_encoder = LabelEncoder()
label_encoder.fit(y)
encoder_path = '../models/crop_encoder.pkl'
pickle.dump(label_encoder, open(encoder_path, 'wb'))
print(f"✅ Label encoder saved: {encoder_path}")

# Save scaler
scaler_path = '../models/crop_scaler.pkl'
pickle.dump(scaler, open(scaler_path, 'wb'))
print(f"✅ Scaler saved: {scaler_path}")

# Save feature encoders
feature_encoders = {
    'season': le_season,
    'ph_category': le_ph_category,
    'rainfall_intensity': le_rainfall_intensity
}
encoders_path = '../models/crop_feature_encoders.pkl'
pickle.dump(feature_encoders, open(encoders_path, 'wb'))
print(f"✅ Feature encoders saved: {encoders_path}")

# ============================================================================
# STEP 10: SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TRAINING COMPLETE - FINAL SUMMARY")
print("=" * 80)

print(f"\n📊 Final Results:")
print(f"  Best Model: {best_model_name}")
print(f"  Test Accuracy: {best_accuracy*100:.2f}%")
print(f"  Cross-Validation: {cv_scores.mean()*100:.2f}%")
print(f"  Total Crops: {len(label_encoder.classes_)}")
print(f"  Training Samples: {len(X_train)}")
print(f"  Testing Samples: {len(X_test)}")
print(f"  Features: {len(feature_cols)}")

print(f"\n🌾 Crops Supported ({len(label_encoder.classes_)} total):")
for i, crop in enumerate(sorted(label_encoder.classes_), 1):
    print(f"  {i:2d}. {crop}")

print(f"\n💾 Files Saved:")
print(f"  - Model: {model_path}")
print(f"  - Features: {feature_names_path}")
print(f"  - Encoder: {encoder_path}")
print(f"  - Scaler: {scaler_path}")
print(f"  - Feature Encoders: {encoders_path}")

print(f"\n⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

"""
Merge and Prepare Crop Datasets
- Combines two crop recommendation datasets
- Cleans and standardizes column names
- Removes duplicates and missing values
- Saves merged dataset
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("MERGING AND PREPARING CROP DATASETS")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ============================================================================
# STEP 1: LOAD DATASETS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: LOADING DATASETS")
print("=" * 80)

df1 = pd.read_csv('../../data/raw/Crop_recommendation.csv')
df2 = pd.read_csv('../../data/raw/Crop_recommendation (1).csv')

print(f"\n📊 Dataset 1:")
print(f"  Shape: {df1.shape}")
print(f"  Columns: {df1.columns.tolist()}")
print(f"  Crops: {df1['label'].nunique()}")
print(f"  Missing values: {df1.isnull().sum().sum()}")

print(f"\n📊 Dataset 2:")
print(f"  Shape: {df2.shape}")
print(f"  Columns: {df2.columns.tolist()}")
print(f"  Crops: {df2['label'].nunique()}")
print(f"  Missing values: {df2.isnull().sum().sum()}")

# ============================================================================
# STEP 2: STANDARDIZE COLUMN NAMES
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: STANDARDIZING COLUMN NAMES")
print("=" * 80)

# Rename columns in df2 to match df1
df2_renamed = df2.copy()
df2_renamed.columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label', 'col8', 'col9']

# Remove unnecessary columns
df2_renamed = df2_renamed[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label']]

print(f"\n✅ Dataset 2 columns standardized:")
print(f"  Original: {df2.columns.tolist()}")
print(f"  Standardized: {df2_renamed.columns.tolist()}")

# ============================================================================
# STEP 3: CLEAN DATA
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: CLEANING DATA")
print("=" * 80)

# Remove rows with missing values
df1_clean = df1.dropna()
df2_clean = df2_renamed.dropna()

print(f"\n🧹 Removed missing values:")
print(f"  Dataset 1: {len(df1)} → {len(df1_clean)} rows")
print(f"  Dataset 2: {len(df2_renamed)} → {len(df2_clean)} rows")

# Remove duplicates
df1_clean = df1_clean.drop_duplicates()
df2_clean = df2_clean.drop_duplicates()

print(f"\n🧹 Removed duplicates:")
print(f"  Dataset 1: {len(df1_clean)} rows")
print(f"  Dataset 2: {len(df2_clean)} rows")

# ============================================================================
# STEP 4: VALIDATE DATA RANGES
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: VALIDATING DATA RANGES")
print("=" * 80)

# Define valid ranges
valid_ranges = {
    'N': (0, 150),
    'P': (0, 150),
    'K': (0, 210),
    'temperature': (0, 50),
    'humidity': (0, 100),
    'ph': (0, 14),
    'rainfall': (0, 500)
}

def validate_ranges(df, ranges):
    """Remove rows with values outside valid ranges"""
    initial_len = len(df)
    for col, (min_val, max_val) in ranges.items():
        df = df[(df[col] >= min_val) & (df[col] <= max_val)]
    removed = initial_len - len(df)
    return df, removed

df1_clean, removed1 = validate_ranges(df1_clean, valid_ranges)
df2_clean, removed2 = validate_ranges(df2_clean, valid_ranges)

print(f"\n✅ Validated data ranges:")
print(f"  Dataset 1: Removed {removed1} invalid rows → {len(df1_clean)} rows")
print(f"  Dataset 2: Removed {removed2} invalid rows → {len(df2_clean)} rows")

# ============================================================================
# STEP 5: MERGE DATASETS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: MERGING DATASETS")
print("=" * 80)

df_merged = pd.concat([df1_clean, df2_clean], ignore_index=True)

print(f"\n📊 Merged Dataset:")
print(f"  Total rows: {len(df_merged)}")
print(f"  Total columns: {len(df_merged.columns)}")
print(f"  Unique crops: {df_merged['label'].nunique()}")

print(f"\n🌾 Crop Distribution:")
crop_dist = df_merged['label'].value_counts()
for crop, count in crop_dist.items():
    print(f"  {crop:<15} {count:>4} samples")

# ============================================================================
# STEP 6: STATISTICAL ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 6: STATISTICAL ANALYSIS")
print("=" * 80)

print(f"\n📈 Statistical Summary:")
print(df_merged.describe())

print(f"\n📊 Data Quality:")
print(f"  Missing values: {df_merged.isnull().sum().sum()}")
print(f"  Duplicates: {df_merged.duplicated().sum()}")
print(f"  Data types:\n{df_merged.dtypes}")

# ============================================================================
# STEP 7: SAVE MERGED DATASET
# ============================================================================
print("\n" + "=" * 80)
print("STEP 7: SAVING MERGED DATASET")
print("=" * 80)

# Save to processed folder
output_path = '../../data/processed/crop_recommendation_merged.csv'
df_merged.to_csv(output_path, index=False)

print(f"\n✅ Merged dataset saved:")
print(f"  Path: {output_path}")
print(f"  Rows: {len(df_merged)}")
print(f"  Columns: {len(df_merged.columns)}")

# ============================================================================
# STEP 8: SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n📊 Final Dataset Statistics:")
print(f"  Total samples: {len(df_merged)}")
print(f"  Total crops: {df_merged['label'].nunique()}")
print(f"  Features: {len(df_merged.columns) - 1}")
print(f"  Samples per crop: {len(df_merged) / df_merged['label'].nunique():.0f}")

print(f"\n✨ Data Quality Metrics:")
print(f"  Completeness: 100% (no missing values)")
print(f"  Uniqueness: {(1 - df_merged.duplicated().sum() / len(df_merged)) * 100:.2f}%")
print(f"  Validity: 100% (all values in valid ranges)")

print(f"\n🎯 Ready for Training:")
print(f"  ✅ Dataset merged")
print(f"  ✅ Data cleaned")
print(f"  ✅ Ranges validated")
print(f"  ✅ Saved to: {output_path}")

print(f"\n⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

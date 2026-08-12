"""
Test disease detection API with multiple images
"""

import requests
import os
import json

# Test images from different classes
test_images = [
    'kisansathi/data/processed/diseases/data/Cassava___healthy/100000.jpg',
    'kisansathi/data/processed/diseases/data/Cassava___mosaic_disease/100001.jpg',
    'kisansathi/data/processed/diseases/data/Potato___early_blight/100002.jpg',
]

print("=" * 80)
print("TESTING DISEASE DETECTION API - MULTIPLE IMAGES")
print("=" * 80)

# Find actual test images
actual_test_images = []
for root, dirs, files in os.walk('kisansathi/data/processed/diseases/data'):
    if files:
        for f in files[:1]:  # Take first file from each directory
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                actual_test_images.append(os.path.join(root, f))
                if len(actual_test_images) >= 3:
                    break
    if len(actual_test_images) >= 3:
        break

print(f"\nFound {len(actual_test_images)} test images")

for test_image_path in actual_test_images:
    if os.path.exists(test_image_path):
        print(f"\n{'='*80}")
        print(f"Testing: {os.path.basename(os.path.dirname(test_image_path))}")
        print(f"File: {os.path.basename(test_image_path)}")
        
        try:
            with open(test_image_path, 'rb') as f:
                files = {'files': (os.path.basename(test_image_path), f, 'image/jpeg')}
                
                response = requests.post(
                    'http://localhost:5000/api/disease-predict',
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('predictions'):
                        pred = result['predictions'][0]
                        print(f"✅ Prediction: {pred.get('disease')}")
                        print(f"   Confidence: {pred.get('confidence')}%")
                        if pred.get('management'):
                            print(f"   Management: {pred['management']['description']}")
                else:
                    print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ API TESTING COMPLETE")
print("=" * 80)

"""
Test ML-based disease detection
"""

import os
import sys
from utils.disease_detection_ml import detect_disease_ml

# Test with a sample image
test_image_path = 'kisansathi/data/processed/diseases/data/Apple___alternaria_leaf_spot/112921.jpg'

if os.path.exists(test_image_path):
    print("=" * 80)
    print("TESTING ML DISEASE DETECTION")
    print("=" * 80)
    print(f"\nTest image: {test_image_path}")
    
    # Open image file
    with open(test_image_path, 'rb') as f:
        result = detect_disease_ml(f)
    
    print("\nPrediction Result:")
    print(f"Success: {result['success']}")
    
    if result['success']:
        print(f"Disease: {result['disease']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"\nManagement Recommendations:")
        for rec in result['management']['management']:
            print(f"  - {rec}")
        print(f"\nTop 5 Probabilities:")
        sorted_probs = sorted(result['all_probabilities'].items(), 
                            key=lambda x: x[1], reverse=True)[:5]
        for disease, prob in sorted_probs:
            print(f"  {disease}: {prob}%")
    else:
        print(f"Error: {result['error']}")
    
    print("\n" + "=" * 80)
else:
    print(f"Test image not found: {test_image_path}")

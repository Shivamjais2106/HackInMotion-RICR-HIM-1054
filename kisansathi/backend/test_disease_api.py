"""
Test disease detection API endpoint
"""

import requests
import os

# Test image path
test_image_path = 'kisansathi/data/processed/diseases/data/Apple___alternaria_leaf_spot/112921.jpg'

if os.path.exists(test_image_path):
    print("=" * 80)
    print("TESTING DISEASE DETECTION API")
    print("=" * 80)
    
    # Prepare file for upload
    with open(test_image_path, 'rb') as f:
        files = {'files': (os.path.basename(test_image_path), f, 'image/jpeg')}
        
        # Send request to API
        try:
            response = requests.post(
                'http://localhost:5000/api/disease-predict',
                files=files,
                timeout=30
            )
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"\nResponse:")
            import json
            result = response.json()
            print(json.dumps(result, indent=2))
            
            if response.status_code == 200:
                print("\n✅ API working correctly!")
                if result.get('predictions'):
                    pred = result['predictions'][0]
                    print(f"\nPrediction Details:")
                    print(f"  Disease: {pred.get('disease')}")
                    print(f"  Confidence: {pred.get('confidence')}%")
                    if pred.get('management'):
                        print(f"  Management: {pred['management']['description']}")
            else:
                print("\n❌ API returned error")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
else:
    print(f"Test image not found: {test_image_path}")

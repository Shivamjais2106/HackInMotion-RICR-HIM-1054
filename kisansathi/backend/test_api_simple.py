"""
Simple API test to verify disease detection works
"""

import requests
import os

# Find a test image
test_image = None
for root, dirs, files in os.walk('kisansathi/data/processed/diseases/data'):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            test_image = os.path.join(root, f)
            break
    if test_image:
        break

if test_image:
    print(f"Testing with image: {test_image}")
    print(f"File size: {os.path.getsize(test_image)} bytes")
    
    try:
        with open(test_image, 'rb') as f:
            files = {'files': (os.path.basename(test_image), f, 'image/jpeg')}
            
            print("\nSending request to http://localhost:5000/api/disease-predict")
            response = requests.post(
                'http://localhost:5000/api/disease-predict',
                files=files,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ SUCCESS!")
                print(f"Disease: {result.get('most_common_disease')}")
                print(f"Predictions: {len(result.get('predictions', []))}")
            else:
                print(f"\n❌ ERROR: {response.status_code}")
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No test image found")

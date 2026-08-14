"""
Simple API test to verify disease detection works
"""

import requests
import os

# Find a test image
test_image = None
<<<<<<< HEAD
for root, dirs, files in os.walk("kisansathi/data/processed/diseases/data"):
    for f in files:
        if f.lower().endswith((".jpg", ".jpeg", ".png")):
=======
for root, dirs, files in os.walk('kisansathi/data/processed/diseases/data'):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
            test_image = os.path.join(root, f)
            break
    if test_image:
        break

if test_image:
    print(f"Testing with image: {test_image}")
    print(f"File size: {os.path.getsize(test_image)} bytes")
<<<<<<< HEAD

    try:
        with open(test_image, "rb") as f:
            files = {"files": (os.path.basename(test_image), f, "image/jpeg")}

            print("\nSending request to http://localhost:5000/api/disease-predict")
            response = requests.post("http://localhost:5000/api/disease-predict", files=files, timeout=30)

            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")

            if response.status_code == 200:
                result = response.json()
                print("\n✅ SUCCESS!")
=======
    
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
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
                print(f"Disease: {result.get('most_common_disease')}")
                print(f"Predictions: {len(result.get('predictions', []))}")
            else:
                print(f"\n❌ ERROR: {response.status_code}")
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        traceback.print_exc()
else:
    print("No test image found")

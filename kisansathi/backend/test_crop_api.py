"""
Test crop recommendation API
"""

import requests
import json

print("=" * 80)
print("TESTING CROP RECOMMENDATION API")
print("=" * 80)

# Test data
<<<<<<< HEAD
test_data = {"N": 90, "P": 42, "K": 43, "temperature": 20.87, "humidity": 82.0, "ph": 6.0, "rainfall": 202.9}

print("\nTest Data:")
=======
test_data = {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.87,
    "humidity": 82.0,
    "ph": 6.0,
    "rainfall": 202.9
}

print(f"\nTest Data:")
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
print(json.dumps(test_data, indent=2))

try:
    print("\nSending request to http://localhost:5000/api/recommendations/crop")
    print("(This may take 30-40 seconds as it calls Gemini API for explanation...)")
<<<<<<< HEAD
    response = requests.post("http://localhost:5000/api/recommendations/crop", json=test_data, timeout=60)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS!")
        print("Response:")
=======
    response = requests.post(
        'http://localhost:5000/api/recommendations/crop',
        json=test_data,
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"Response:")
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        print(json.dumps(result, indent=2))
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

print("\n" + "=" * 80)

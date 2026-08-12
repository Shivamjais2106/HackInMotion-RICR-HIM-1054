"""
Test crop recommendation API
"""

import requests
import json

print("=" * 80)
print("TESTING CROP RECOMMENDATION API")
print("=" * 80)

# Test data
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
print(json.dumps(test_data, indent=2))

try:
    print("\nSending request to http://localhost:5000/api/recommendations/crop")
    print("(This may take 30-40 seconds as it calls Gemini API for explanation...)")
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
        print(json.dumps(result, indent=2))
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

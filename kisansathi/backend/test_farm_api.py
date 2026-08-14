"""
Integration Tests — Farm Profile & Recommendation APIs
=======================================================
Tests the core farm decision support endpoints:
  - POST /api/auth/register
  - POST /api/auth/login
  - GET/POST /api/farm-profile
  - GET /api/farm-profile/irrigation-advice
  - POST /api/recommendations/crop
  - GET /api/market/prices

Run: pytest test_farm_api.py -v

Author: Shivam Jaiswal
"""

import json
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
@pytest.fixture
def client():
    """Create a Flask test client from app_enhanced."""
    try:
        from app_enhanced import app
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        app.config["TESTING"] = True
        app.config["JWT_SECRET_KEY"] = "test-secret"
        with app.test_client() as c:
            yield c
    except Exception:
        pytest.skip("app_enhanced not importable in this environment")


@pytest.fixture
def test_mobile():
    import time
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    return f"99{int(time.time()) % 100000000:08d}"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["status"] == "healthy"


def test_status(client):
    r = client.get("/api/status")
    assert r.status_code in (200, 503)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
def test_register_and_login(client, test_mobile):
    # Register
    payload = {
        "name": "Test Farmer",
        "email": f"{test_mobile}@test.com",
        "mobile": test_mobile,
        "password": "Test@1234",
        "agriculture_type": "crops",
    }
<<<<<<< HEAD
    r = client.post("/api/auth/register", data=json.dumps(payload), content_type="application/json")
    assert r.status_code in (201, 503)  # 503 if DB unavailable in CI

    # Login
    r = client.post(
        "/api/auth/login",
        data=json.dumps({"mobile": test_mobile, "password": "Test@1234"}),
        content_type="application/json",
    )
=======
    r = client.post("/api/auth/register",
                    data=json.dumps(payload),
                    content_type="application/json")
    assert r.status_code in (201, 503)  # 503 if DB unavailable in CI

    # Login
    r = client.post("/api/auth/login",
                    data=json.dumps({"mobile": test_mobile, "password": "Test@1234"}),
                    content_type="application/json")
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    assert r.status_code in (200, 401, 503)


def test_register_missing_fields(client):
<<<<<<< HEAD
    r = client.post("/api/auth/register", data=json.dumps({"email": "x@x.com"}), content_type="application/json")
=======
    r = client.post("/api/auth/register",
                    data=json.dumps({"email": "x@x.com"}),
                    content_type="application/json")
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# Market Prices
# ---------------------------------------------------------------------------

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
def test_market_prices_endpoint(client):
    r = client.get("/api/market/prices")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["success"] is True
    assert isinstance(data["prices"], list)
    assert len(data["prices"]) > 0


def test_single_commodity_price(client):
    r = client.get("/api/market/prices/wheat")
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        data = json.loads(r.data)
        assert "modal_price" in data


# ---------------------------------------------------------------------------
# Crop Recommendation
# ---------------------------------------------------------------------------

<<<<<<< HEAD

def test_crop_recommendation(client):
    payload = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 25,
        "humidity": 80,
        "ph": 6.5,
        "rainfall": 200,
    }
    r = client.post("/api/recommendations/crop", data=json.dumps(payload), content_type="application/json")
=======
def test_crop_recommendation(client):
    payload = {
        "N": 90, "P": 42, "K": 43,
        "temperature": 25, "humidity": 80,
        "ph": 6.5, "rainfall": 200,
    }
    r = client.post("/api/recommendations/crop",
                    data=json.dumps(payload),
                    content_type="application/json")
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    assert r.status_code in (200, 400, 500)


def test_crop_recommendation_missing_fields(client):
<<<<<<< HEAD
    r = client.post("/api/recommendations/crop", data=json.dumps({"N": 90}), content_type="application/json")
=======
    r = client.post("/api/recommendations/crop",
                    data=json.dumps({"N": 90}),
                    content_type="application/json")
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
def test_weather_endpoint(client):
    r = client.get("/api/weather/Delhi")
    assert r.status_code in (200, 503)

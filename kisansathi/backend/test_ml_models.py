"""
ML Model Smoke Tests — KisanSathi
====================================
Validates that trained .pkl model files load correctly and
return sensible predictions for known inputs.

Run: pytest test_ml_models.py -v

Author: Shivam Jaiswal
"""

import pytest
import os


MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")


def _model_exists(filename: str) -> bool:
    return os.path.isfile(os.path.join(MODEL_DIR, filename))


# ── Crop Recommendation ───────────────────────────────────────────────────────


@pytest.mark.skipif(
    not _model_exists("crop_recommendation_model_xgboost_comprehensive.pkl"), reason="Model file not present"
)
def test_crop_recommendation_ml():
    from utils.crop_recommendation_ml import get_crop_recommendation_ml

    result = get_crop_recommendation_ml(N=90, P=42, K=43, temperature=25.0, humidity=80.0, ph=6.5, rainfall=200.0)
    assert result["success"] is True
    assert len(result["recommendations"]) >= 1
    top = result["recommendations"][0]
    assert "crop" in top
    assert 0 <= top["confidence"] <= 1


# ── Seasonal Crop ─────────────────────────────────────────────────────────────


@pytest.mark.skipif(not _model_exists("seasonal_crop_model.pkl"), reason="Model file not present")
def test_seasonal_crop_recommendation():
    from utils.seasonal_crop_recommender import get_seasonal_crop_recommendation

    recs = get_seasonal_crop_recommendation(
        N=60, P=40, K=40, temperature=22.0, humidity=65.0, ph=6.5, rainfall=120.0, month="June", top_n=3
    )
    assert isinstance(recs, list)
    assert len(recs) >= 1


# ── Fertilizer Recommendation ─────────────────────────────────────────────────


@pytest.mark.skipif(not _model_exists("fertilizer_model_xgboost.pkl"), reason="Model file not present")
def test_fertilizer_recommendation():
    from utils.fertilizer_recommendation import get_fertilizer_recommendation

    result = get_fertilizer_recommendation(
        nitrogen=20,
        phosphorus=30,
        potassium=40,
        temperature=25.0,
        humidity=60.0,
        moisture=40.0,
        soil_type="Loamy",
        crop_type="Wheat",
    )
    assert result is not None


# ── Irrigation Engine (pure logic — no model file) ───────────────────────────


def test_irrigation_engine_high_need():
    from utils.irrigation_engine import compute_irrigation_need

    result = compute_irrigation_need(t_mean=38, t_max=43, t_min=33, rainfall_mm=0, soil_type="Sandy", crop="wheat")
    assert result["irrigation_need_mm"] > 0
    assert result["risk_level"] in ("high", "medium")


def test_irrigation_engine_no_need():
    from utils.irrigation_engine import compute_irrigation_need

    result = compute_irrigation_need(t_mean=22, t_max=27, t_min=17, rainfall_mm=20, soil_type="Clay", crop="rice")
    assert result["risk_level"] in ("low", "medium")


# ── Market Prices (pure logic — no model file) ───────────────────────────────


def test_market_reference_price():
    from utils.market_prices import get_reference_price, get_trade_advice

    price = get_reference_price("wheat")
    assert price is not None
    assert price["modal_price"] > 0

    advice = get_trade_advice("wheat", price["modal_price"])
    assert isinstance(advice, str)
    assert len(advice) > 0


def test_market_all_prices():
    from utils.market_prices import get_all_prices

    prices = get_all_prices()
    assert len(prices) >= 10

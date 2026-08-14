"""
Mandi prices, MSP reference and bulk lookup.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

import requests

from flask import Blueprint
from flask import request, jsonify
from datetime import datetime
from extensions import limiter
from decorators import error_handler

import logging

logger = logging.getLogger(__name__)

market_bp = Blueprint("market", __name__)


# Static mandi reference prices (based on real MSP/APMC data 2025-26)
MANDI_BASE_PRICES = {
    "wheat": {"min": 2275, "max": 2500, "unit": "per quintal", "msP": 2275},
    "rice": {"min": 2300, "max": 2600, "unit": "per quintal", "msP": 2300},
    "maize": {"min": 2090, "max": 2400, "unit": "per quintal", "msP": 2090},
    "soybean": {"min": 4892, "max": 5500, "unit": "per quintal", "msP": 4892},
    "cotton": {"min": 7121, "max": 8000, "unit": "per quintal", "msP": 7121},
    "mustard": {"min": 5950, "max": 6500, "unit": "per quintal", "msP": 5950},
    "groundnut": {"min": 6783, "max": 7500, "unit": "per quintal", "msP": 6783},
    "chickpea": {"min": 5440, "max": 6200, "unit": "per quintal", "msP": 5440},
    "lentil": {"min": 6425, "max": 7200, "unit": "per quintal", "msP": 6425},
    "onion": {"min": 800, "max": 2500, "unit": "per quintal", "msP": None},
    "potato": {"min": 600, "max": 1800, "unit": "per quintal", "msP": None},
    "tomato": {"min": 500, "max": 3000, "unit": "per quintal", "msP": None},
    "sugarcane": {"min": 340, "max": 380, "unit": "per quintal", "msP": 340},
    "turmeric": {"min": 9000, "max": 14000, "unit": "per quintal", "msP": None},
    "chilli": {"min": 8000, "max": 16000, "unit": "per quintal", "msP": None},
    "barley": {"min": 1735, "max": 2100, "unit": "per quintal", "msP": 1735},
    "jowar": {"min": 3371, "max": 3800, "unit": "per quintal", "msP": 3371},
    "bajra": {"min": 2625, "max": 3000, "unit": "per quintal", "msP": 2625},
    "sunflower": {"min": 7280, "max": 8000, "unit": "per quintal", "msP": 7280},
    "sesame": {"min": 8635, "max": 10000, "unit": "per quintal", "msP": 8635},
}


def get_live_market_price(commodity: str):
    """
    Fetch live price from data.gov.in AGMARKNET API.
    Falls back to MSP-based estimate if API unavailable.
    """
    try:
        # data.gov.in commodity prices API (free, no key required)
        commodity_clean = commodity.lower().strip()
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": "resource:9ef84268-d588-465a-a308-a864a43d0070",
            "format": "json",
            "filters[commodity]": commodity.capitalize(),
            "limit": 5,
            "sort[arrival_date]": "desc",
        }
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            data = r.json()
            records = data.get("records", [])
            if records:
                prices = [float(rec.get("modal_price", 0)) for rec in records if rec.get("modal_price")]
                if prices:
                    avg = sum(prices) / len(prices)
                    return {
                        "source": "AGMARKNET (data.gov.in)",
                        "modal_price": round(avg),
                        "min_price": min(prices),
                        "max_price": max(prices),
                        "records": len(prices),
                        "live": True,
                    }
    except Exception as e:
        logger.warning(f"Live price fetch failed for {commodity}: {e}")

    # Fallback to MSP/reference prices
    base = MANDI_BASE_PRICES.get(commodity.lower(), {})
    if base:
        import random

        # Simulate realistic price fluctuation ±10%
        modal = round(
            base["min"] + (base["max"] - base["min"]) * 0.5 + random.uniform(-base["min"] * 0.05, base["min"] * 0.05)
        )
        return {
            "source": "MSP Reference (GoI 2025-26)",
            "modal_price": modal,
            "min_price": base["min"],
            "max_price": base["max"],
            "msp": base.get("msP"),
            "live": False,
        }
    return None


@market_bp.route("/api/market/prices", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
def get_market_prices():
    """Get current mandi prices for all major commodities"""
    prices = []
    for commodity, base in MANDI_BASE_PRICES.items():
        price_data = get_live_market_price(commodity)
        if price_data:
            prices.append(
                {
                    "commodity": commodity.capitalize(),
                    "commodity_key": commodity,
                    "unit": base["unit"],
                    "msp": base.get("msP"),
                    **price_data,
                }
            )
    return jsonify(
        {
            "success": True,
            "prices": prices,
            "total": len(prices),
            "timestamp": datetime.now().isoformat(),
            "note": "Prices in INR. Live data from AGMARKNET where available, else MSP reference.",
        }
    ), 200


@market_bp.route("/api/market/prices/<commodity>", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
def get_commodity_price(commodity):
    """Get price for a specific commodity"""
    price_data = get_live_market_price(commodity)
    if not price_data:
        return jsonify({"error": f"Commodity {commodity} not found"}), 404
    base = MANDI_BASE_PRICES.get(commodity.lower(), {})
    return jsonify(
        {
            "success": True,
            "commodity": commodity.capitalize(),
            "unit": base.get("unit", "per quintal"),
            "msp": base.get("msP"),
            "timestamp": datetime.now().isoformat(),
            **price_data,
        }
    ), 200


@market_bp.route("/api/market/prices/bulk", methods=["POST"])
@limiter.limit("20 per hour")
@error_handler
def get_bulk_prices():
    """Get prices for a list of commodities (for farm profile crops)"""
    data = request.get_json() or {}
    commodities = data.get("commodities", list(MANDI_BASE_PRICES.keys())[:10])
    prices = []
    for commodity in commodities:
        price_data = get_live_market_price(commodity)
        if price_data:
            base = MANDI_BASE_PRICES.get(commodity.lower(), {})
            prices.append(
                {
                    "commodity": commodity.capitalize(),
                    "commodity_key": commodity.lower(),
                    "unit": base.get("unit", "per quintal"),
                    "msp": base.get("msP"),
                    **price_data,
                }
            )
    return jsonify(
        {"success": True, "prices": prices, "total": len(prices), "timestamp": datetime.now().isoformat()}
    ), 200

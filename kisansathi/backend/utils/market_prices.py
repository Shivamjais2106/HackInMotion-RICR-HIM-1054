"""
Market Price Intelligence Module — KisanSathi
Fetches live commodity prices from AGMARKNET (data.gov.in).
Falls back to MSP reference prices when the live API is unavailable.

Author: Rustam Ali
"""

import logging
import random
import requests

logger = logging.getLogger(__name__)

# MSP / APMC reference prices (GoI 2025-26 season)
MANDI_BASE_PRICES: dict[str, dict] = {
    "wheat":     {"min": 2275,  "max": 2500,  "unit": "per quintal", "msp": 2275},
    "rice":      {"min": 2300,  "max": 2600,  "unit": "per quintal", "msp": 2300},
    "maize":     {"min": 2090,  "max": 2400,  "unit": "per quintal", "msp": 2090},
    "soybean":   {"min": 4892,  "max": 5500,  "unit": "per quintal", "msp": 4892},
    "cotton":    {"min": 7121,  "max": 8000,  "unit": "per quintal", "msp": 7121},
    "mustard":   {"min": 5950,  "max": 6500,  "unit": "per quintal", "msp": 5950},
    "groundnut": {"min": 6783,  "max": 7500,  "unit": "per quintal", "msp": 6783},
    "chickpea":  {"min": 5440,  "max": 6200,  "unit": "per quintal", "msp": 5440},
    "lentil":    {"min": 6425,  "max": 7200,  "unit": "per quintal", "msp": 6425},
    "onion":     {"min": 800,   "max": 2500,  "unit": "per quintal", "msp": None},
    "potato":    {"min": 600,   "max": 1800,  "unit": "per quintal", "msp": None},
    "tomato":    {"min": 500,   "max": 3000,  "unit": "per quintal", "msp": None},
    "sugarcane": {"min": 340,   "max": 380,   "unit": "per quintal", "msp": 340},
    "turmeric":  {"min": 9000,  "max": 14000, "unit": "per quintal", "msp": None},
    "chilli":    {"min": 8000,  "max": 16000, "unit": "per quintal", "msp": None},
    "barley":    {"min": 1735,  "max": 2100,  "unit": "per quintal", "msp": 1735},
    "jowar":     {"min": 3371,  "max": 3800,  "unit": "per quintal", "msp": 3371},
    "bajra":     {"min": 2625,  "max": 3000,  "unit": "per quintal", "msp": 2625},
    "sunflower": {"min": 7280,  "max": 8000,  "unit": "per quintal", "msp": 7280},
    "sesame":    {"min": 8635,  "max": 10000, "unit": "per quintal", "msp": 8635},
}

# AGMARKNET API resource ID on data.gov.in (free, no key needed)
AGMARKNET_API_URL = (
    "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
)


def get_live_price(commodity: str) -> dict | None:
    """
    Try to fetch live modal price from AGMARKNET.
    Returns a dict with price details, or None on failure.
    """
    try:
        params = {
            "api-key": "resource:9ef84268-d588-465a-a308-a864a43d0070",
            "format": "json",
            "filters[commodity]": commodity.capitalize(),
            "limit": 5,
            "sort[arrival_date]": "desc",
        }
        resp = requests.get(AGMARKNET_API_URL, params=params, timeout=5)
        if resp.status_code == 200:
            records = resp.json().get("records", [])
            prices = [
                float(r["modal_price"])
                for r in records
                if r.get("modal_price")
            ]
            if prices:
                avg_modal = round(sum(prices) / len(prices))
                return {
                    "source": "AGMARKNET (data.gov.in)",
                    "modal_price": avg_modal,
                    "min_price": min(prices),
                    "max_price": max(prices),
                    "records_used": len(prices),
                    "live": True,
                }
    except Exception as exc:
        logger.warning("Live price fetch failed for %s: %s", commodity, exc)
    return None


def get_reference_price(commodity: str) -> dict | None:
    """Return an MSP-based estimate with ±5 % realistic fluctuation."""
    base = MANDI_BASE_PRICES.get(commodity.lower())
    if not base:
        return None
    mid = (base["min"] + base["max"]) / 2
    jitter = mid * random.uniform(-0.05, 0.05)
    modal = int(round(mid + jitter))
    return {
        "source": "MSP Reference (GoI 2025-26)",
        "modal_price": modal,
        "min_price": base["min"],
        "max_price": base["max"],
        "msp": base["msp"],
        "live": False,
    }


def get_commodity_price(commodity: str) -> dict | None:
    """Get price for a single commodity (live → fallback)."""
    price = get_live_price(commodity)
    if price:
        return price
    return get_reference_price(commodity)


def get_all_prices() -> list[dict]:
    """Return price data for every commodity in the reference table."""
    results = []
    for name, base in MANDI_BASE_PRICES.items():
        price = get_commodity_price(name)
        if price:
            results.append({
                "commodity": name.capitalize(),
                "commodity_key": name,
                "unit": base["unit"],
                "msp": base["msp"],
                **price,
            })
    return results


def get_trade_advice(commodity: str, modal_price: int) -> str:
    """
    Simple trade advisory based on modal price vs MSP.
    Returns a short human-readable recommendation.
    """
    base = MANDI_BASE_PRICES.get(commodity.lower(), {})
    msp = base.get("msp")
    max_price = base.get("max", modal_price)

    if msp and modal_price < msp:
        return "Price below MSP — consider government procurement channels."
    if modal_price >= max_price * 0.90:
        return "Optimal selling window — prices near seasonal high."
    if modal_price >= max_price * 0.75:
        return "Good selling opportunity — prices above average."
    return "Hold if possible — prices are below average for this season."

# v1.1 — added get_trade_advice for sell/hold/MSP advisory

"""
Weather Alerts Module — KisanSathi
====================================
Generates farming-specific risk alerts from WeatherAPI.com data.
Called by /api/weather/<location>/alerts endpoint.

Author: Bhoomi Kesharwani
"""

from __future__ import annotations
import logging
import os
import requests

logger = logging.getLogger(__name__)

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY", "")
BASE_URL = "https://api.weatherapi.com/v1"


def _fetch_current(location: str) -> dict | None:
    """Fetch current weather JSON from WeatherAPI.com."""
    if not WEATHERAPI_KEY:
        logger.warning("WEATHERAPI_KEY not set — alerts unavailable")
        return None
    try:
        r = requests.get(
            f"{BASE_URL}/current.json",
            params={"key": WEATHERAPI_KEY, "q": location},
            timeout=5,
        )
        if r.status_code == 200:
            return r.json()
        logger.error("WeatherAPI returned %s for %s", r.status_code, location)
    except requests.exceptions.Timeout:
        logger.error("WeatherAPI timeout for %s", location)
    except Exception as exc:
        logger.error("WeatherAPI error: %s", exc)
    return None


def get_farming_alerts(location: str) -> list[dict]:
    """
    Return a list of farming-relevant weather alert dicts.

    Each alert has:
      - type       : str  (FROST | HEAT | HUMIDITY | WIND | RAIN)
      - severity   : str  (critical | high | medium | low)
      - message    : str  (human-readable advice)
    """
    data = _fetch_current(location)
    if not data:
        return []

    c = data.get("current", {})
    temp = c.get("temp_c", 25)
    humidity = c.get("humidity", 60)
    wind_kph = c.get("wind_kph", 10)
    precip_mm = c.get("precip_mm", 0)

    alerts: list[dict] = []

    # --- Temperature alerts ---
    if temp <= 0:
        alerts.append(
            {
                "type": "FROST",
                "severity": "critical",
                "message": "Frost warning — protect sensitive crops immediately with covers.",
            }
        )
    elif temp <= 4:
        alerts.append(
            {
                "type": "COLD_STRESS",
                "severity": "high",
                "message": "Cold stress risk — cover seedlings and nurseries overnight.",
            }
        )
    elif temp >= 42:
        alerts.append(
            {
                "type": "EXTREME_HEAT",
                "severity": "critical",
                "message": "Extreme heat — irrigate early morning, provide shade for vegetables.",
            }
        )
    elif temp >= 38:
        alerts.append(
            {
                "type": "HEAT_STRESS",
                "severity": "high",
                "message": "Heat stress expected — increase irrigation frequency today.",
            }
        )

    # --- Humidity alerts (fungal risk) ---
    if humidity >= 90:
        alerts.append(
            {
                "type": "FUNGAL_RISK",
                "severity": "high",
                "message": (
                    "Very high humidity — high risk of fungal diseases (late blight, rust, powdery mildew). "
                    "Apply preventive fungicide today."
                ),
            }
        )
    elif humidity >= 80:
        alerts.append(
            {
                "type": "FUNGAL_RISK",
                "severity": "medium",
                "message": "Elevated humidity — monitor crops for early fungal symptoms.",
            }
        )

    # --- Wind alerts ---
    if wind_kph >= 50:
        alerts.append(
            {
                "type": "HIGH_WIND",
                "severity": "high",
                "message": "Strong winds — support tall crops, delay pesticide spraying.",
            }
        )

    # --- Heavy rain ---
    if precip_mm >= 20:
        alerts.append(
            {
                "type": "HEAVY_RAIN",
                "severity": "medium",
                "message": (f"Heavy rainfall ({precip_mm} mm) — check field drainage, delay fertilizer application."),
            }
        )

    return alerts

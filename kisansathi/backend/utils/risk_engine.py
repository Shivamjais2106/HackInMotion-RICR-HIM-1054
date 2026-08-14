"""
Weather Risk Engine — KisanSathi
==================================
Requirement 3: Weather-Based Irrigation & Risk Engine

Converts raw WeatherAPI.com data into actionable farming decisions:
  - Irrigation guidance: "irrigate today" / "skip — rain expected"
  - Risk alerts: frost, extreme heat, fungal risk, heavy rain, drought

Author: Rustam Ali
"""

from __future__ import annotations
import os
import logging
import requests

logger = logging.getLogger(__name__)

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY", "")
BASE = "https://api.weatherapi.com/v1"


def _forecast(location: str, days: int = 3) -> dict | None:
    if not WEATHERAPI_KEY:
        return None
    try:
        r = requests.get(
            f"{BASE}/forecast.json",
            params={"key": WEATHERAPI_KEY, "q": location, "days": days},
            timeout=6,
        )
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        logger.error("WeatherAPI forecast error: %s", e)
        return None


def get_irrigation_decision(location: str, soil_type: str = "Loamy") -> dict:
    """
    Returns a clear irrigation decision for today based on:
    - Today's evapotranspiration estimate
    - Rainfall in next 48 hours
    - Soil water retention

    Returns dict with:
      decision     : "irrigate_today" | "skip_rain_expected" | "monitor"
      message      : human-readable guidance
      reason       : technical explanation
      next_rain_mm : expected rainfall in next 48 h
    """
    data = _forecast(location, days=3)

    # Soil retention factor
    retention = {
        "Sandy": 0.30, "Red": 0.45, "Loamy": 0.60,
        "Black": 0.75, "Clay": 0.80, "Clayey": 0.80,
    }.get(soil_type, 0.60)

    if not data:
        return {
            "decision": "monitor",
            "message": "Weather data unavailable — check soil moisture manually.",
            "reason": "WeatherAPI key not set or service unreachable.",
            "next_rain_mm": 0,
            "live": False,
        }

    today = data["forecast"]["forecastday"][0]["day"]
    tomorrow = data["forecast"]["forecastday"][1]["day"] if len(data["forecast"]["forecastday"]) > 1 else {}

    today_rain = today.get("totalprecip_mm", 0)
    tomorrow_rain = tomorrow.get("totalprecip_mm", 0)
    next_48h_rain = today_rain + tomorrow_rain

    temp_max = today.get("maxtemp_c", 30)
    humidity = today.get("avghumidity", 60)

    # Simplified ET0 (Hargreaves)
    temp_min = today.get("mintemp_c", 20)
    temp_mean = (temp_max + temp_min) / 2
    et0 = max(0, 0.0023 * (temp_mean + 17.8) * ((temp_max - temp_min) ** 0.5) * 15 * 0.408)
    effective_rain = today_rain * 0.8 * retention
    net_need = max(0, round(et0 - effective_rain, 1))

    if next_48h_rain >= 10:
        decision = "skip_rain_expected"
        message = f"No need to irrigate — {next_48h_rain:.0f} mm rain expected in next 48 hours."
        reason = f"Forecasted rainfall ({next_48h_rain:.0f} mm) covers crop water need."
    elif net_need > 3.5 or (temp_max >= 38 and humidity < 40):
        decision = "irrigate_today"
        message = f"Irrigate today — net water need is {net_need} mm/day, no rain expected."
        reason = f"ET0={et0:.1f} mm, effective rain={effective_rain:.1f} mm, deficit={net_need} mm."
    elif net_need > 1.5:
        decision = "irrigate_within_24h"
        message = f"Plan irrigation within 24 hours — moderate water deficit ({net_need} mm/day)."
        reason = "Soil moisture will drop below safe threshold by tomorrow."
    else:
        decision = "monitor"
        message = "Soil moisture adequate — monitor and irrigate if leaves show wilting."
        reason = f"Net irrigation need low ({net_need} mm/day)."

    return {
        "decision": decision,
        "message": message,
        "reason": reason,
        "net_need_mm": net_need,
        "next_rain_mm": round(next_48h_rain, 1),
        "temp_max": temp_max,
        "humidity": humidity,
        "soil_type": soil_type,
        "live": True,
    }


def get_risk_alerts(location: str) -> list[dict]:
    """
    Returns list of farming risk alerts for the location.
    Each alert: {type, severity, message, action}
    """
    data = _forecast(location, days=1)
    if not data:
        return []

    c = data.get("current", {})
    temp = c.get("temp_c", 25)
    humidity = c.get("humidity", 60)
    wind_kph = c.get("wind_kph", 10)
    precip_mm = c.get("precip_mm", 0)

    alerts: list[dict] = []

    if temp <= 0:
        alerts.append({
            "type": "FROST",
            "severity": "critical",
            "message": "Frost warning — protect crops immediately.",
            "action": "Cover sensitive crops. Use mulching or plastic covers overnight.",
        })
    elif temp <= 4:
        alerts.append({
            "type": "COLD_STRESS",
            "severity": "high",
            "message": "Cold stress likely below 4°C.",
            "action": "Protect nurseries and seedlings with covers.",
        })

    if temp >= 42:
        alerts.append({
            "type": "EXTREME_HEAT",
            "severity": "critical",
            "message": f"Extreme heat alert — {temp}°C.",
            "action": "Irrigate early morning. Provide shade for vegetables.",
        })
    elif temp >= 38:
        alerts.append({
            "type": "HEAT_STRESS",
            "severity": "high",
            "message": f"Heat stress at {temp}°C.",
            "action": "Increase irrigation frequency. Avoid spraying pesticides.",
        })

    if humidity >= 90:
        alerts.append({
            "type": "FUNGAL_RISK",
            "severity": "high",
            "message": "Very high humidity — fungal disease risk (late blight, rust).",
            "action": "Apply preventive fungicide. Improve field drainage.",
        })
    elif humidity >= 80:
        alerts.append({
            "type": "FUNGAL_RISK",
            "severity": "medium",
            "message": "Elevated humidity — monitor for fungal symptoms.",
            "action": "Inspect leaves for spots. Ensure good airflow between rows.",
        })

    if wind_kph >= 50:
        alerts.append({
            "type": "HIGH_WIND",
            "severity": "high",
            "message": f"Strong winds {wind_kph:.0f} km/h.",
            "action": "Support tall crops. Delay spraying operations.",
        })

    if precip_mm >= 25:
        alerts.append({
            "type": "HEAVY_RAIN",
            "severity": "medium",
            "message": f"Heavy rainfall {precip_mm:.0f} mm.",
            "action": "Check field drainage. Delay fertilizer application by 2 days.",
        })

    return alerts

"""
Irrigation Decision Engine — KisanSathi
========================================
Computes daily irrigation need using the Hargreaves ET0 model,
adjusted for soil water-retention and effective rainfall.

Author: Bhoomi Kesharwani
"""

from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

# Crop coefficients (Kc) by growth stage — FAO-56 standard values
CROP_KC: dict[str, dict[str, float]] = {
<<<<<<< HEAD
    "wheat": {"initial": 0.30, "mid": 1.15, "late": 0.40},
    "rice": {"initial": 1.05, "mid": 1.20, "late": 0.90},
    "maize": {"initial": 0.30, "mid": 1.20, "late": 0.60},
    "cotton": {"initial": 0.35, "mid": 1.20, "late": 0.70},
    "soybean": {"initial": 0.40, "mid": 1.15, "late": 0.50},
    "potato": {"initial": 0.45, "mid": 1.10, "late": 0.75},
    "tomato": {"initial": 0.60, "mid": 1.15, "late": 0.80},
    "onion": {"initial": 0.50, "mid": 1.00, "late": 0.75},
    "sugarcane": {"initial": 0.40, "mid": 1.25, "late": 0.75},
    "chickpea": {"initial": 0.40, "mid": 1.00, "late": 0.35},
    "mustard": {"initial": 0.35, "mid": 1.10, "late": 0.40},
    "groundnut": {"initial": 0.40, "mid": 1.15, "late": 0.60},
    "default": {"initial": 0.40, "mid": 1.10, "late": 0.60},
=======
    "wheat":     {"initial": 0.30, "mid": 1.15, "late": 0.40},
    "rice":      {"initial": 1.05, "mid": 1.20, "late": 0.90},
    "maize":     {"initial": 0.30, "mid": 1.20, "late": 0.60},
    "cotton":    {"initial": 0.35, "mid": 1.20, "late": 0.70},
    "soybean":   {"initial": 0.40, "mid": 1.15, "late": 0.50},
    "potato":    {"initial": 0.45, "mid": 1.10, "late": 0.75},
    "tomato":    {"initial": 0.60, "mid": 1.15, "late": 0.80},
    "onion":     {"initial": 0.50, "mid": 1.00, "late": 0.75},
    "sugarcane": {"initial": 0.40, "mid": 1.25, "late": 0.75},
    "chickpea":  {"initial": 0.40, "mid": 1.00, "late": 0.35},
    "mustard":   {"initial": 0.35, "mid": 1.10, "late": 0.40},
    "groundnut": {"initial": 0.40, "mid": 1.15, "late": 0.60},
    "default":   {"initial": 0.40, "mid": 1.10, "late": 0.60},
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
}

# Soil water-retention factor (0–1)
SOIL_RETENTION: dict[str, float] = {
<<<<<<< HEAD
    "Sandy": 0.30,
    "Red": 0.45,
    "Loamy": 0.60,
    "Alluvial": 0.62,
    "Black": 0.75,
    "Clay": 0.80,
    "Clayey": 0.80,
}


def hargreaves_et0(t_mean: float, t_max: float, t_min: float, ra: float = 15.0) -> float:
=======
    "Sandy":   0.30,
    "Red":     0.45,
    "Loamy":   0.60,
    "Alluvial":0.62,
    "Black":   0.75,
    "Clay":    0.80,
    "Clayey":  0.80,
}


def hargreaves_et0(t_mean: float, t_max: float, t_min: float,
                   ra: float = 15.0) -> float:
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    """
    Hargreaves (1985) reference evapotranspiration.
    ET0 in mm/day.

    Parameters
    ----------
    t_mean  : mean daily temperature (°C)
    t_max   : daily max temperature (°C)
    t_min   : daily min temperature (°C)
    ra      : extra-terrestrial radiation (MJ/m²/day) — default 15 (India avg)
    """
    td = max(t_max - t_min, 0.0)
<<<<<<< HEAD
    et0 = 0.0023 * (t_mean + 17.8) * (td**0.5) * ra * 0.408
=======
    et0 = 0.0023 * (t_mean + 17.8) * (td ** 0.5) * ra * 0.408
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    return max(round(et0, 2), 0.0)


def compute_irrigation_need(
    t_mean: float,
    t_max: float,
    t_min: float,
    rainfall_mm: float,
    soil_type: str = "Loamy",
    crop: str = "default",
    growth_stage: str = "mid",
) -> dict:
    """
    Compute net irrigation need for one day.

    Returns a dict with:
      - et0_mm          : reference ET0
      - etc_mm          : crop ET (ET0 × Kc)
      - effective_rain  : rainfall available to crop (×0.8 efficiency)
      - irrigation_need : max(0, ETc − effective_rain)
      - risk_level      : 'high' | 'medium' | 'low'
      - advice          : list[str]
    """
    et0 = hargreaves_et0(t_mean, t_max, t_min)

    kc_table = CROP_KC.get(crop.lower(), CROP_KC["default"])
    kc = kc_table.get(growth_stage, kc_table["mid"])
    etc = round(et0 * kc, 2)

    retention = SOIL_RETENTION.get(soil_type, 0.60)
    effective_rain = round(rainfall_mm * 0.80 * retention, 2)

    need = max(0.0, round(etc - effective_rain, 2))

    # Risk classification
    if need > 4.0:
        risk = "high"
    elif need > 2.0:
        risk = "medium"
    else:
        risk = "low"

    advice: list[str] = []
    if rainfall_mm >= 10:
        advice.append(f"Recent rainfall ({rainfall_mm} mm) covers most irrigation needs today.")
    if need > 4.0:
        advice.append("Irrigate today — high water stress expected.")
    elif need > 2.0:
        advice.append("Plan irrigation within the next 24–48 hours.")
    else:
        advice.append("No irrigation needed today — soil moisture adequate.")

    if soil_type in ("Sandy", "Red"):
        advice.append(f"{soil_type} soil drains fast — prefer frequent, light irrigations.")
    elif soil_type in ("Clay", "Clayey", "Black"):
        advice.append(f"{soil_type} soil retains water — avoid over-irrigation and check drainage.")

    return {
        "et0_mm": et0,
        "crop_kc": kc,
        "etc_mm": etc,
        "rainfall_mm": rainfall_mm,
        "effective_rain_mm": effective_rain,
        "irrigation_need_mm": need,
        "risk_level": risk,
        "soil_type": soil_type,
        "crop": crop,
        "growth_stage": growth_stage,
        "advice": advice,
    }


<<<<<<< HEAD
def weather_risk_alerts(temp: float, humidity: float, wind_kph: float = 10.0) -> list[dict]:
=======
def weather_risk_alerts(temp: float, humidity: float,
                        wind_kph: float = 10.0) -> list[dict]:
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    """
    Generate weather-based risk alerts relevant to farming.
    Returns a list of alert dicts with type, severity, message.
    """
    alerts: list[dict] = []

    if temp <= 0:
<<<<<<< HEAD
        alerts.append(
            {
                "type": "FROST",
                "severity": "critical",
                "message": "Frost risk — protect sensitive crops immediately.",
            }
        )
    elif temp <= 4:
        alerts.append(
            {
                "type": "COLD_STRESS",
                "severity": "high",
                "message": "Cold stress likely — cover seedlings and nurseries.",
            }
        )

    if temp >= 42:
        alerts.append(
            {
                "type": "EXTREME_HEAT",
                "severity": "critical",
                "message": "Extreme heat — irrigate early morning, provide shade if possible.",
            }
        )
    elif temp >= 38:
        alerts.append(
            {
                "type": "HEAT_STRESS",
                "severity": "high",
                "message": "Heat stress — increase irrigation frequency.",
            }
        )

    if humidity >= 90:
        alerts.append(
            {
                "type": "FUNGAL_RISK",
                "severity": "high",
                "message": "High humidity — high risk of fungal diseases (late blight, rust). Apply preventive fungicide.",
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

    if wind_kph >= 50:
        alerts.append(
            {
                "type": "HIGH_WIND",
                "severity": "high",
                "message": "Strong winds — support tall crops, delay pesticide spraying.",
            }
        )
=======
        alerts.append({
            "type": "FROST",
            "severity": "critical",
            "message": "Frost risk — protect sensitive crops immediately.",
        })
    elif temp <= 4:
        alerts.append({
            "type": "COLD_STRESS",
            "severity": "high",
            "message": "Cold stress likely — cover seedlings and nurseries.",
        })

    if temp >= 42:
        alerts.append({
            "type": "EXTREME_HEAT",
            "severity": "critical",
            "message": "Extreme heat — irrigate early morning, provide shade if possible.",
        })
    elif temp >= 38:
        alerts.append({
            "type": "HEAT_STRESS",
            "severity": "high",
            "message": "Heat stress — increase irrigation frequency.",
        })

    if humidity >= 90:
        alerts.append({
            "type": "FUNGAL_RISK",
            "severity": "high",
            "message": "High humidity — high risk of fungal diseases (late blight, rust). Apply preventive fungicide.",
        })
    elif humidity >= 80:
        alerts.append({
            "type": "FUNGAL_RISK",
            "severity": "medium",
            "message": "Elevated humidity — monitor crops for early fungal symptoms.",
        })

    if wind_kph >= 50:
        alerts.append({
            "type": "HIGH_WIND",
            "severity": "high",
            "message": "Strong winds — support tall crops, delay pesticide spraying.",
        })
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6

    return alerts

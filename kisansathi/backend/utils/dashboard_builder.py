"""
Unified Dashboard Builder — KisanSathi
========================================
Requirement 6: Unified Farmer Dashboard

Aggregates all data sources into one response for the dashboard:
  - Farm profile
  - Live weather + irrigation decision
  - Weather risk alerts
  - Market prices for farmer's crops
  - Latest crop health log

Called by GET /api/dashboard/unified (JWT required)

Author: Rustam Ali
"""

from __future__ import annotations
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def build_dashboard(db, user_id: str) -> dict:
    """
    Builds the full unified dashboard payload for a farmer.

    Returns dict with sections:
      farm_profile, weather, irrigation, alerts,
      market_prices, health_summary, today_actions
    """
    result: dict = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "farm_profile": None,
        "weather": None,
        "irrigation": None,
        "alerts": [],
        "market_prices": [],
        "health_summary": None,
        "today_actions": [],
        "errors": [],
    }

    # ── 1. Farm Profile ──────────────────────────────────────────────────────
    try:
        profile = db["farm_profiles"].find_one({"user_id": user_id})
        if profile:
            profile["_id"] = str(profile["_id"])
            result["farm_profile"] = profile
    except Exception as e:
        logger.error("Dashboard: farm profile error: %s", e)
        result["errors"].append("Farm profile unavailable")

    location = (result["farm_profile"] or {}).get("location", "Delhi")
    soil_type = (result["farm_profile"] or {}).get("soil_type", "Loamy")
    active_crops = (result["farm_profile"] or {}).get("active_crops", [])

    # ── 2. Weather + Irrigation ──────────────────────────────────────────────
    try:
        from utils.weather_integration import get_weather_for_farming, get_weather_forecast
        from utils.risk_engine import get_irrigation_decision, get_risk_alerts

        weather = get_weather_for_farming(location)
        result["weather"] = weather

        irrigation = get_irrigation_decision(location, soil_type)
        result["irrigation"] = irrigation

        alerts = get_risk_alerts(location)
        result["alerts"] = alerts

    except Exception as e:
        logger.error("Dashboard: weather error: %s", e)
        result["errors"].append("Weather data temporarily unavailable")

    # ── 3. Market Prices for farmer's crops ─────────────────────────────────
    try:
        from utils.price_trends import get_price_summary
        from utils.market_prices import MANDI_BASE_PRICES

        # Show farmer's crops first, then top 5 others
        crops_to_show = [c.lower() for c in active_crops if c.lower() in MANDI_BASE_PRICES]
        if len(crops_to_show) < 5:
            extras = [k for k in list(MANDI_BASE_PRICES.keys())[:8] if k not in crops_to_show]
            crops_to_show += extras[: 5 - len(crops_to_show)]

        for crop in crops_to_show[:8]:
            try:
                summary = get_price_summary(crop)
                if summary:
                    result["market_prices"].append(summary)
            except Exception:
                pass

    except Exception as e:
        logger.error("Dashboard: market prices error: %s", e)
        result["errors"].append("Market prices temporarily unavailable")

    # ── 4. Latest Crop Health Log ────────────────────────────────────────────
    try:
        log = db["health_logs"].find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        if log:
            log["_id"] = str(log["_id"])
            result["health_summary"] = {
                "crop": log.get("crop", ""),
                "disease": log.get("disease", ""),
                "severity": log.get("severity", "low"),
                "observation": log.get("observation", ""),
                "date": log.get("created_at", ""),
            }
    except Exception as e:
        logger.error("Dashboard: health log error: %s", e)
        result["errors"].append("Crop health data unavailable")

    # ── 5. Today's Priority Actions ──────────────────────────────────────────
    actions = []

    irr = result.get("irrigation") or {}
    if irr.get("decision") == "irrigate_today":
        actions.append({
            "priority": "high",
            "icon": "💧",
            "action": "Irrigate today",
            "detail": irr.get("message", ""),
        })
    elif irr.get("decision") == "irrigate_within_24h":
        actions.append({
            "priority": "medium",
            "icon": "💧",
            "action": "Plan irrigation within 24 hours",
            "detail": irr.get("message", ""),
        })

    for alert in result["alerts"]:
        if alert.get("severity") in ("critical", "high"):
            actions.append({
                "priority": alert["severity"],
                "icon": "⚠️",
                "action": alert["type"].replace("_", " ").title(),
                "detail": alert.get("action", alert.get("message", "")),
            })

    health = result.get("health_summary") or {}
    if health.get("severity") in ("high", "critical"):
        actions.append({
            "priority": "high",
            "icon": "🌿",
            "action": f"Treat {health.get('crop', 'crop')} — {health.get('disease', 'disease detected')}",
            "detail": "Check recent crop health log for recommended action.",
        })

    # Sort: critical > high > medium > low
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    actions.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
    result["today_actions"] = actions[:5]  # top 5 actions

    return result

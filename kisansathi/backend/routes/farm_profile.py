"""
Farm profile, irrigation advice and health logs.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from database import db
from decorators import error_handler

import logging

logger = logging.getLogger(__name__)

farm_profile_bp = Blueprint("farm_profile", __name__)


@farm_profile_bp.route("/api/farm-profile", methods=["GET"])
@jwt_required()
@error_handler
def get_farm_profile():
    """Get farm profile for logged-in farmer"""
    user_id = get_jwt_identity()
    profile = db["farm_profiles"].find_one({"user_id": user_id})
    if not profile:
        return jsonify({"profile": None, "message": "No farm profile found"}), 200
    profile["_id"] = str(profile["_id"])
    return jsonify({"success": True, "profile": profile}), 200


@farm_profile_bp.route("/api/farm-profile", methods=["POST"])
@jwt_required()
@error_handler
def create_farm_profile():
    """Create or update farm profile"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    profile = {
        "user_id": user_id,
        "farm_name": data.get("farm_name", ""),
        "location": data.get("location", ""),
        "state": data.get("state", ""),
        "district": data.get("district", ""),
        "land_size_acres": float(data.get("land_size_acres", 0)),
        "soil_type": data.get("soil_type", ""),
        "water_source": data.get("water_source", ""),
        "irrigation_type": data.get("irrigation_type", ""),
        "active_crops": data.get("active_crops", []),
        "past_crops": data.get("past_crops", []),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "updated_at": datetime.now().isoformat(),
    }

    existing = db["farm_profiles"].find_one({"user_id": user_id})
    if existing:
        db["farm_profiles"].update_one({"user_id": user_id}, {"$set": profile})
        msg = "Farm profile updated"
    else:
        profile["created_at"] = datetime.now().isoformat()
        db["farm_profiles"].insert_one(profile)
        msg = "Farm profile created"

    logger.info(f"Farm profile saved for user {user_id}")
    return jsonify({"success": True, "message": msg, "profile": {k: v for k, v in profile.items() if k != "_id"}}), 200


@farm_profile_bp.route("/api/farm-profile/irrigation-advice", methods=["GET"])
@jwt_required()
@error_handler
def get_irrigation_advice():
    """Get farm-profile-specific irrigation advice based on soil + weather"""
    user_id = get_jwt_identity()
    profile = db["farm_profiles"].find_one({"user_id": user_id})
    if not profile:
        return jsonify({"error": "Farm profile not found. Please set up your farm profile first."}), 404

    location = profile.get("location", "Central India")
    soil_type = profile.get("soil_type", "Loamy")
    active_crops = profile.get("active_crops", [])
    irrigation_type = profile.get("irrigation_type", "flood")

    # Get weather for farm location
    weather_live = True
    try:
        from utils.weather_integration import get_weather_for_farming

        weather = get_weather_for_farming(location)
        if weather:
            humidity = weather.get("humidity", 60)
            rainfall = weather.get("rainfall_mm", 0)
            temp = weather.get("temperature", 25)
        else:
            raise ValueError("Empty weather response")
    except Exception:
        humidity, rainfall, temp = 60, 0, 25
        weather_live = False

    # Soil water retention mapping
    retention = {"Sandy": 0.3, "Loamy": 0.6, "Clay": 0.8, "Clayey": 0.8, "Black": 0.75, "Red": 0.5}
    ret = retention.get(soil_type, 0.5)

    # Irrigation need calculation
    et0 = 0.0023 * (temp + 17.8) * (45 - humidity) * 0.408  # simplified Hargreaves
    effective_rain = rainfall * 0.8
    irrigation_need = max(0, round(et0 - effective_rain / 10, 2))

    schedule = []
    if irrigation_need > 3:
        schedule = ["Irrigate today — high water demand", "Check soil moisture daily"]
    elif irrigation_need > 1:
        schedule = ["Irrigate in 2-3 days", "Monitor crop leaves for wilting"]
    else:
        schedule = ["No irrigation needed today", "Soil moisture adequate"]

    if soil_type in ["Sandy"]:
        schedule.append("Sandy soil: irrigate more frequently in smaller amounts")
    elif soil_type in ["Clay", "Clayey", "Black"]:
        schedule.append("Clay soil: avoid over-irrigation, check drainage")

    return jsonify(
        {
            "success": True,
            "farm_location": location,
            "soil_type": soil_type,
            "active_crops": active_crops,
            "irrigation_type": irrigation_type,
            "weather": {"temperature": temp, "humidity": humidity, "rainfall_mm": rainfall},
            "weather_live": weather_live,
            "weather_warning": None
            if weather_live
            else "Live weather unavailable — using average estimates. Advice may be less accurate.",
            "irrigation_need_mm_per_day": irrigation_need,
            "schedule": schedule,
            "water_retention": f"{int(ret * 100)}%",
            "timestamp": datetime.now().isoformat(),
        }
    ), 200


@farm_profile_bp.route("/api/farm-profile/health-logs", methods=["GET"])
@jwt_required()
@error_handler
def get_health_logs():
    """Get crop health observation logs for this farm"""
    user_id = get_jwt_identity()
    logs = list(db["health_logs"].find({"user_id": user_id}).sort("created_at", -1).limit(20))
    for log in logs:
        log["_id"] = str(log["_id"])
    return jsonify({"success": True, "logs": logs, "total": len(logs)}), 200


@farm_profile_bp.route("/api/farm-profile/health-logs", methods=["POST"])
@jwt_required()
@error_handler
def add_health_log():
    """Add a crop health observation log"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    log = {
        "user_id": user_id,
        "crop": data.get("crop", ""),
        "observation": data.get("observation", ""),
        "disease": data.get("disease", ""),
        "severity": data.get("severity", "low"),
        "action_taken": data.get("action_taken", ""),
        "image_url": data.get("image_url", ""),
        "created_at": datetime.now().isoformat(),
    }
    result = db["health_logs"].insert_one(log)
    return jsonify({"success": True, "log_id": str(result.inserted_id), "message": "Health log added"}), 201

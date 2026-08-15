"""
Location detection, weather, forecast and alerts.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

import requests

from flask import Blueprint
from flask import request, jsonify
from datetime import datetime
from extensions import limiter
from decorators import error_handler, redis_cache
from integrations import (
    get_weather_for_farming,
    get_farming_recommendations_based_on_weather,
    get_weather_alerts,
    get_weather_forecast,
)

import logging

logger = logging.getLogger(__name__)

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/api/location/detect", methods=["GET"])
@limiter.limit("60 per hour")
@error_handler
def detect_location():
    """Detect user's location from IP address"""
    try:
        # Get client IP
        client_ip = request.remote_addr

        # Simple IP-based location detection
        # This is a fallback - in production, use a proper geolocation service
        location_map = {
            "127.0.0.1": "Delhi",
            "localhost": "Delhi",
        }

        # Check if it's a local IP
        if client_ip in location_map:
            city = location_map[client_ip]
        else:
            # For other IPs, try to detect based on common patterns
            # This is a simple fallback
            city = "Delhi"

        logger.info(f"Location detected for IP {client_ip}: {city}")

        return jsonify({"success": True, "city": city, "ip": client_ip, "method": "ip-based"}), 200
    except Exception as e:
        logger.error(f"Error detecting location: {e}")
        return jsonify({"success": False, "city": "Delhi", "error": str(e)}), 200


@weather_bp.route("/api/location/from-gps", methods=["POST"])
@limiter.limit("60 per hour")
@error_handler
def detect_location_from_gps():
    """Detect location from GPS coordinates using reverse geocoding"""
    try:
        data = request.get_json()
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not latitude or not longitude:
            return jsonify({"success": False, "error": "Latitude and longitude required"}), 400

        logger.info(f"Reverse geocoding for GPS: {latitude}, {longitude}")

        # Use OpenStreetMap Nominatim for reverse geocoding
        try:
            response = requests.get(
                f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}",
                timeout=5,
                headers={"User-Agent": "KisanSathi/1.0"},
            )

            if response.status_code == 200:
                location_data = response.json()
                address = location_data.get("address", {})

                # Try to get city, town, or village
                city = address.get("city") or address.get("town") or address.get("village") or "Delhi"
                state = address.get("state", "")
                country = address.get("country", "India")

                logger.info(f"Reverse geocoding result: {city}, {state}, {country}")

                return jsonify(
                    {
                        "success": True,
                        "city": city,
                        "state": state,
                        "country": country,
                        "latitude": latitude,
                        "longitude": longitude,
                        "method": "gps-based",
                    }
                ), 200
            else:
                logger.error(f"Nominatim returned status {response.status_code}")
                return jsonify({"success": False, "error": "Reverse geocoding failed", "city": "Delhi"}), 200
        except requests.exceptions.Timeout:
            logger.error("Nominatim request timed out")
            return jsonify({"success": False, "error": "Reverse geocoding timeout", "city": "Delhi"}), 200
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return jsonify({"success": False, "error": str(e), "city": "Delhi"}), 200

    except Exception as e:
        logger.error(f"Error in GPS location detection: {e}")
        return jsonify({"success": False, "error": str(e), "city": "Delhi"}), 200


@weather_bp.route("/api/weather/<location>", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@redis_cache(expire=600)
def get_weather(location):
    """Get current weather for a location (cached in Redis)"""
    try:
        weather = get_weather_for_farming(location)
        forecast = get_weather_forecast(location)

        if not weather:
            logger.warning(f"Weather API returned empty data for {location}")
            return jsonify(
                {
                    "error": "Weather data unavailable for this location. Check the location name or try again later.",
                    "location": location,
                    "weather": None,
                    "forecast": [],
                    "service_status": "unavailable",
                }
            ), 503

        logger.info(f"Weather retrieved for {location}")
        return jsonify(
            {
                "location": location,
                "weather": weather,
                "forecast": forecast or [],
                "timestamp": datetime.now().isoformat(),
                "cached": False,
            }
        ), 200
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        return jsonify({"error": f"Weather service error: {str(e)}. Please try again later."}), 503


@weather_bp.route("/api/weather/<location>/forecast", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@redis_cache(expire=600)
def get_forecast(location):
    """Get 5-day weather forecast for a location (cached in Redis)"""
    try:
        forecast = get_weather_forecast(location)

        logger.info(f"Forecast retrieved for {location}")

        return jsonify(
            {"location": location, "forecast": forecast, "timestamp": datetime.now().isoformat(), "cached": False}
        ), 200
    except Exception as e:
        logger.error(f"Error getting forecast: {e}")
        return jsonify({"error": f"Forecast retrieval failed: {str(e)}"}), 500


@weather_bp.route("/api/weather/<location>/recommendations", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@redis_cache(expire=600)
def get_weather_recommendations(location):
    """Get farming recommendations based on weather (cached in Redis)"""
    try:
        recommendations = get_farming_recommendations_based_on_weather(location)

        logger.info(f"Weather recommendations generated for {location}")

        return jsonify(
            {
                "location": location,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat(),
                "cached": False,
            }
        ), 200
    except Exception as e:
        logger.error(f"Error getting weather recommendations: {e}")
        return jsonify({"error": f"Recommendations failed: {str(e)}"}), 500


@weather_bp.route("/api/weather/<location>/alerts", methods=["GET"])
@limiter.limit("30 per hour")
@error_handler
@redis_cache(expire=300)
def get_alerts(location):
    """Get weather alerts for a location (cached in Redis)"""
    try:
        alerts = get_weather_alerts(location)

        logger.info(f"Weather alerts retrieved for {location}")

        return jsonify(
            {
                "location": location,
                "alerts": alerts,
                "total": len(alerts),
                "timestamp": datetime.now().isoformat(),
                "cached": False,
            }
        ), 200
    except Exception as e:
        logger.error(f"Error getting weather alerts: {e}")
        return jsonify({"error": f"Alerts retrieval failed: {str(e)}"}), 500

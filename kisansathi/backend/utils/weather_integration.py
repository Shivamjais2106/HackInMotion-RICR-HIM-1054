import requests
import os
import logging

logger = logging.getLogger(__name__)


def get_weather_for_farming(location="Delhi"):
    try:
        k = os.getenv("WEATHERAPI_KEY", "")
        if not k:
            return {
                "location": "Default",
                "temperature": 25,
                "humidity": 60,
                "feels_like": 25,
                "temp_min": 20,
                "temp_max": 30,
                "wind_speed": 10,
                "condition": "Clear",
                "rainfall": 0,
            }
        r = requests.get(f"https://api.weatherapi.com/v1/current.json?key={k}&q={location}", timeout=5)
        if r.status_code == 200:
            d = r.json()
            c = d["current"]
            return {
                "location": d["location"]["name"],
                "temperature": c["temp_c"],
                "feels_like": c["feelslike_c"],
                "humidity": c["humidity"],
                "wind_speed": c["wind_kph"],
                "condition": c["condition"]["text"],
                "rainfall": c["precip_mm"],
                "temp_min": c["temp_c"] - 2,
                "temp_max": c["temp_c"] + 2,
            }
        return {
            "location": "Default",
            "temperature": 25,
            "humidity": 60,
            "feels_like": 25,
            "temp_min": 20,
            "temp_max": 30,
            "wind_speed": 10,
            "condition": "Clear",
            "rainfall": 0,
        }
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        return {
            "location": "Default",
            "temperature": 25,
            "humidity": 60,
            "feels_like": 25,
            "temp_min": 20,
            "temp_max": 30,
            "wind_speed": 10,
            "condition": "Clear",
            "rainfall": 0,
        }


def get_weather_forecast(location="Delhi"):
    """Get 5-day weather forecast"""
    try:
        k = os.getenv("WEATHERAPI_KEY", "")
        if not k:
            logger.warning("WEATHERAPI_KEY not set")
            return []
        r = requests.get(
            f"https://api.weatherapi.com/v1/forecast.json?key={k}&q={location}&days=5&aqi=no",
            timeout=5,
        )
        if r.status_code == 200:
            d = r.json()
            forecast = []
            for day in d["forecast"]["forecastday"]:
                forecast.append(
                    {
                        "date": day["date"],
                        "day": day["date"].split("-")[2],
                        "temp_min": day["day"]["mintemp_c"],
                        "temp_max": day["day"]["maxtemp_c"],
                        "temp_avg": day["day"]["avgtemp_c"],
                        "humidity_avg": day["day"]["avghumidity"],
                        "description": day["day"]["condition"]["text"],
                        "wind_speed_avg": day["day"]["avgvis_km"],
                    }
                )
            logger.info(f"Forecast retrieved for {location}: {len(forecast)} days")
            return forecast
        logger.error(f"Forecast API returned status {r.status_code}")
        return []
    except Exception as e:
        logger.error(f"Error getting forecast: {e}", exc_info=True)
        return []


def get_farming_recommendations_based_on_weather(location="Delhi"):
    try:
        k = os.getenv("WEATHERAPI_KEY", "")
        if not k:
            return ["Check soil", "Monitor crops"]
        r = requests.get(f"https://api.weatherapi.com/v1/current.json?key={k}&q={location}", timeout=5)
        if r.status_code == 200:
            d = r.json()
            c = d["current"]
            rec = []
            if c["temp_c"] < 10:
                rec.append("Protect from frost")
            elif c["temp_c"] > 35:
                rec.append("Increase irrigation")
            if c["humidity"] > 80:
                rec.append("Watch for fungal diseases")
            elif c["humidity"] < 30:
                rec.append("Increase irrigation")
            return rec if rec else ["Conditions good"]
        return ["Check soil"]
    except Exception as e:
        logger.error(f"Error getting farming recommendations: {e}")
        return ["Check soil"]


def get_weather_alerts(location="Delhi"):
    try:
        k = os.getenv("WEATHERAPI_KEY", "")
        if not k:
            return []
        r = requests.get(f"https://api.weatherapi.com/v1/current.json?key={k}&q={location}", timeout=5)
        if r.status_code == 200:
            d = r.json()
            c = d["current"]
            a = []
            if c["temp_c"] < 0:
                a.append({"type": "FROST", "severity": "high", "message": "Frost"})
            elif c["temp_c"] > 40:
                a.append({"type": "HEAT", "severity": "high", "message": "Heat"})
            if c["humidity"] > 90:
                a.append({"type": "HUMIDITY", "severity": "medium", "message": "High humidity"})
            return a
        return []
    except Exception as e:
        logger.error(f"Error getting weather alerts: {e}")
        return []


def get_farm_specific_irrigation_advice(location="Delhi", soil_type="loamy", crops=None):
    """
    Combines live weather data with the farm's soil type and crops
    to give irrigation advice specific to that farm profile,
    instead of generic city-level advice.
    """
    if crops is None:
        crops = []

    weather = get_weather_for_farming(location)

    soil_water_retention = {
        "sandy": "low",
        "loamy": "medium",
        "clay": "high",
        "black": "high",
        "red": "medium",
        "alluvial": "medium",
    }
    retention = soil_water_retention.get(soil_type, "medium")

    advice = []
    risk_level = "low"

    if weather["rainfall"] >= 10:
        advice.append(f"Recent rainfall covers irrigation needs for {soil_type} soil today.")
    elif weather["temperature"] >= 35 and retention == "low":
        advice.append(f"{soil_type.capitalize()} soil drains fast and temperature is high — irrigate now.")
        risk_level = "high"
    elif weather["temperature"] >= 30 and retention == "medium":
        advice.append(f"Warm conditions with {soil_type} soil — irrigate within 24 hours.")
        risk_level = "medium"
    elif retention == "high":
        advice.append(f"{soil_type.capitalize()} soil retains water well — irrigation can wait.")
    else:
        advice.append("Conditions are within a safe range for your soil type.")

    if crops:
        advice.append(f"Applies to your registered crops: {', '.join(crops)}.")

    return {
        "location": weather["location"],
        "soil_type": soil_type,
        "risk_level": risk_level,
        "advice": advice,
    }

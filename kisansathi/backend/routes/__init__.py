"""
Feature blueprints for the KisanSathi API.

Each module owns one feature area and keeps the same URL paths the single-file
app served, so registering them all reproduces the original route table.
ALL_BLUEPRINTS is what create_app() iterates over — add a new blueprint here and
it is picked up automatically.
"""

from routes.auth import auth_bp
from routes.cache_admin import cache_admin_bp
from routes.chatbot import chatbot_bp
from routes.community import community_bp
from routes.crop_calendar import crop_calendar_bp
from routes.dashboard_unified import dashboard_unified_bp
from routes.disease import disease_bp
from routes.farm_profile import farm_profile_bp
from routes.fertilizer import fertilizer_bp
from routes.health import health_bp
from routes.livestock import livestock_bp
from routes.market import market_bp
from routes.pest import pest_bp
from routes.recommendations import recommendations_bp
from routes.reminders import reminders_bp
from routes.soil import soil_bp
from routes.tts import tts_bp
from routes.weather import weather_bp

ALL_BLUEPRINTS = (
    health_bp,
    auth_bp,
    community_bp,
    recommendations_bp,
    chatbot_bp,
    livestock_bp,
    weather_bp,
    soil_bp,
    fertilizer_bp,
    crop_calendar_bp,
    disease_bp,
    pest_bp,
    cache_admin_bp,
    reminders_bp,
    tts_bp,
    farm_profile_bp,
    dashboard_unified_bp,
    market_bp,
)

__all__ = ["ALL_BLUEPRINTS"]

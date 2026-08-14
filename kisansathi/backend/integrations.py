"""
Optional integrations for KisanSathi (ML models, weather, Gemini, chatbot...).

Every import is guarded: a missing model file or an unavailable dependency must
degrade one feature, not take the whole API down. The no-op fallbacks keep the
same call signatures and the same {'success': False} response shape the routes
and the frontend already handle.

Consolidated from the top of the old single-file app so the route blueprints
share one definition of what is available instead of each re-guarding it.
"""

import logging

logger = logging.getLogger(__name__)

# --- Core recommenders (hard dependencies) ---------------------------------

from utils.crop_recommendation_ranked import get_crop_recommendation  # noqa: F401
from utils.crop_recommendation_ml import get_crop_recommendation_ml  # noqa: F401
from utils.seasonal_crop_recommender import get_seasonal_crop_recommendation  # noqa: F401
from utils.livestock_disease_detection import get_livestock_detector  # noqa: F401

# --- Chatbot ---------------------------------------------------------------

try:
    from utils.unified_chatbot import get_chatbot_response
except Exception as e:
    logger.warning(f"unified_chatbot import failed (Python 3.14 protobuf issue): {e}")

    def get_chatbot_response(*args, **kwargs):
        return {"response": "Chatbot temporarily unavailable", "success": False}

# --- Voice pipeline --------------------------------------------------------

try:
    from utils.voice_pipeline import extract_info_from_transcript, generate_fertilizer_explanation
except Exception as e:
    logger.warning(f"voice_pipeline import failed: {e}")

    def extract_info_from_transcript(*a, **k):
        return {}

    def generate_fertilizer_explanation(*a, **k):
        return ""

# --- Weather ---------------------------------------------------------------

try:
    from utils.weather_integration import (
        get_weather_for_farming,
        get_farming_recommendations_based_on_weather,
        get_weather_alerts,
        get_weather_forecast,
    )
except ImportError as e:
    logger.warning(f"Weather integration import failed: {e}")
    get_weather_for_farming = lambda x: {}
    get_farming_recommendations_based_on_weather = lambda x: []
    get_weather_alerts = lambda x: []
    get_weather_forecast = lambda x: []

# --- Soil ------------------------------------------------------------------

try:
    from utils.soil_analysis import analyze_soil, get_soil_types, get_crop_types, get_fertilizer_types
except ImportError as e:
    logger.warning(f"Soil analysis import failed: {e}")
    analyze_soil = lambda **kwargs: {}
    get_soil_types = lambda: []
    get_crop_types = lambda: []
    get_fertilizer_types = lambda: []

# --- Fertilizer ------------------------------------------------------------

try:
    from utils.fertilizer_recommendation import get_fertilizer_recommendation
except ImportError as e:
    logger.warning(f"Fertilizer recommendation import failed: {e}")
    get_fertilizer_recommendation = lambda **kwargs: {}

# --- Crop calendar ---------------------------------------------------------

try:
    from utils.crop_calendar import (
        get_crop_calendar,
        get_crops_for_month,
        get_crop_details,
        get_seasonal_activities,
    )
except ImportError as e:
    logger.warning(f"Crop calendar import failed: {e}")
    get_crop_calendar = lambda: {}
    get_crops_for_month = lambda x: []
    get_crop_details = lambda x: {}
    get_seasonal_activities = lambda x: []

# --- Pest management -------------------------------------------------------

try:
    from utils.pest_management import identify_pest, get_all_pests, get_pests_for_crop
except ImportError as e:
    logger.warning(f"Pest management import failed: {e}")
    identify_pest = lambda x: {}
    get_all_pests = lambda: []
    get_pests_for_crop = lambda x: []

# --- Plant disease detection ----------------------------------------------

try:
    from utils.plant_disease_detection import detect_rice_disease, detect_plant_disease
except ImportError as e:
    logger.warning(f"Plant disease detection import failed: {e}")
    detect_rice_disease = lambda x: {"success": False, "error": "Model not available"}
    detect_plant_disease = lambda x: {"success": False, "error": "Model not available"}

try:
    from utils.disease_detection_ml import detect_disease_ml
except ImportError as e:
    logger.warning(f"ML disease detection import failed: {e}")
    detect_disease_ml = lambda x: {"success": False, "error": "Model not available"}

# --- Gemini (generative AI) -----------------------------------------------

try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except Exception:
    genai = None
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not available on Python 3.14 (protobuf issue)")

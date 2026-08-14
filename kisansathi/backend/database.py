"""
Data store connections for KisanSathi (MongoDB + Redis).

Connections are opened once at import and shared by every route module.
Both handles degrade to None when the service is unreachable so the API can
still serve endpoints that do not need them — the same behaviour the single-file
app had before the routes were split into blueprints.
"""

import logging
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

logger = logging.getLogger(__name__)

try:
    from redis_config import init_redis, get_redis  # noqa: F401  (re-exported)
except Exception as e:  # pragma: no cover - optional dependency
    logger.warning(f"redis_config import failed: {e}")

    def init_redis(*args, **kwargs):
        return None

    def get_redis():
        return None


# --- MongoDB ---------------------------------------------------------------

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DATABASE", "kisansathi")

try:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    logger.info(f"✅ Connected to MongoDB: {MONGODB_DB}")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    client = None
    db = None


# --- Redis -----------------------------------------------------------------

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "True").lower() == "true"

if REDIS_ENABLED:
    redis_manager = init_redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
else:
    redis_manager = None
    logger.info("⚠️ Redis disabled in configuration")

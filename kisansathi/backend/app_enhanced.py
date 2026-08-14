#!/usr/bin/env python3
"""
KisanSathi - Enhanced MongoDB Backend

Application factory. Feature routes live in routes/ as blueprints; this module
only wires things together:
- JWT authentication, rate limiting, caching, CORS
- Blueprint registration (see routes.ALL_BLUEPRINTS)
- WebSocket event handlers
- App-level error handlers

`app` and `socketio` stay module-level so `app.py` (and therefore
`gunicorn app:app`) keeps importing the same names.
"""

import logging
import os
from datetime import timedelta

from flask import Flask, jsonify
from flask_cors import CORS

from database import MONGODB_DB, REDIS_HOST, REDIS_PORT, db, redis_manager
from extensions import cache, jwt, limiter, socketio
from routes import ALL_BLUEPRINTS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Blueprints whose dependencies are optional: a missing package must disable one
# feature area, not prevent the API from booting.
try:
    from file_routes import file_bp
except Exception as e:
    logger.warning(f"File routes import failed: {e}")
    file_bp = None

try:
    from dashboard_routes import dashboard_bp
except Exception as e:
    logger.warning(f"Dashboard routes import failed: {e}")
    dashboard_bp = None

try:
    from websocket_events import (
        register_connection_events,
        register_chat_events,
        register_notification_events,
        register_monitoring_events,
    )
except Exception as e:
    logger.warning(f"websocket_events import failed: {e}")

    def register_connection_events(*a, **k):
        pass

    def register_chat_events(*a, **k):
        pass

    def register_notification_events(*a, **k):
        pass

    def register_monitoring_events(*a, **k):
        pass


def register_error_handlers(flask_app):
    """JSON error envelopes — the frontend never expects an HTML error page."""

    @flask_app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @flask_app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500


def log_startup_state(flask_app):
    logger.info("Starting KisanSathi Backend (Enhanced)")
    logger.info(f"Database: {MONGODB_DB}")
    if db is not None:
        logger.info("✅ MongoDB connected and ready!")
    else:
        logger.warning("⚠️ MongoDB not connected - some features may not work")
    logger.info("✅ JWT Authentication enabled!")
    logger.info("✅ Rate Limiting enabled!")
    logger.info("✅ Caching enabled!")

    if redis_manager and redis_manager.connected:
        logger.info("✅ Redis caching enabled!")
        logger.info(f"   Host: {REDIS_HOST}:{REDIS_PORT}")
    else:
        logger.warning("⚠️ Redis not available - using fallback caching")

    logger.info("✅ WebSocket events enabled!")
    api_routes = sum(1 for r in flask_app.url_map.iter_rules() if str(r.rule).startswith('/api/'))
    logger.info(f"✅ {api_routes} API endpoints ready!")


def create_app():
    """Build and configure the Flask application."""
    flask_app = Flask(__name__)
    flask_app.config['JSON_SORT_KEYS'] = False

    # --- Security & performance ---
    flask_app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'kisansathi_secret_key_2024')
    flask_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

    jwt.init_app(flask_app)
    limiter.init_app(flask_app)
    cache.init_app(flask_app, config={'CACHE_TYPE': 'simple'})
    socketio.init_app(flask_app, cors_allowed_origins="*", async_mode='threading')
    CORS(flask_app, resources={r"/api/*": {"origins": "*"}})

    # --- Feature routes ---
    for blueprint in ALL_BLUEPRINTS:
        flask_app.register_blueprint(blueprint)

    if file_bp:
        flask_app.register_blueprint(file_bp)
        logger.info("✅ File handling routes registered")

    if dashboard_bp:
        flask_app.register_blueprint(dashboard_bp)
        logger.info("✅ Dashboard monitoring routes registered")

    register_error_handlers(flask_app)

    # --- WebSocket events ---
    register_connection_events(socketio)
    register_chat_events(socketio)
    register_notification_events(socketio)
    register_monitoring_events(socketio)
    logger.info("✅ WebSocket events registered")

    log_startup_state(flask_app)
    return flask_app


app = create_app()


if __name__ == '__main__':
    if db is None:
        logger.error("❌ MongoDB not connected. Please start MongoDB and try again.")
        exit(1)

    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True
    )

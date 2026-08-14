"""
Flask extension singletons for KisanSathi.

Each extension is constructed unbound here and attached to the application in
create_app() (see app_enhanced.py). Route modules import these directly, which
lets them use @limiter.limit(...) and cache decorators without importing the
app object and creating a circular import.
"""

from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

jwt = JWTManager()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

cache = Cache()

socketio = SocketIO()

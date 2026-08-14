"""
Authentication & Security Middleware — KisanSathi
==================================================
JWT verification, bcrypt password helpers, and security
response headers wired into the Flask app.

Author: Rustam Ali
"""

from __future__ import annotations
import logging
from functools import wraps

import bcrypt
from flask import request, jsonify, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
def hash_password(plain: str) -> str:
    """Hash a plain-text password with bcrypt (12 rounds)."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def needs_upgrade(hashed: str) -> bool:
    """Return True if the stored hash is legacy plain-text (not bcrypt)."""
    return not (hashed.startswith("$2b$") or hashed.startswith("$2a$"))


# ---------------------------------------------------------------------------
# JWT decorators
# ---------------------------------------------------------------------------

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
def jwt_required_custom(f):
    """
    Drop-in decorator that verifies JWT and populates g.user_id.
    Returns 401 with a clear message on missing / invalid token.
    """
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            g.user_id = get_jwt_identity()
        except Exception as exc:
            logger.warning("JWT verification failed: %s", exc)
<<<<<<< HEAD
            return jsonify(
                {
                    "error": "Authentication required.",
                    "hint": "Include a valid Bearer token in the Authorization header.",
                }
            ), 401
        return f(*args, **kwargs)

=======
            return jsonify({
                "error": "Authentication required.",
                "hint": "Include a valid Bearer token in the Authorization header.",
            }), 401
        return f(*args, **kwargs)
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    return decorated


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
def add_security_headers(app):
    """
    Register an after-request hook that injects OWASP-recommended
    security headers on every response.
    """
<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
    @app.after_request
    def _set_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
<<<<<<< HEAD
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
=======
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
        return response

    logger.info("Security headers registered.")


# ---------------------------------------------------------------------------
# Rate-limit helper
# Used by Flask-Limiter to identify real client IP behind proxy
# ---------------------------------------------------------------------------

<<<<<<< HEAD

=======
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
def get_real_ip() -> str:
    """
    Return the real client IP, honouring X-Forwarded-For when
    running behind a reverse proxy (Render, Vercel, Nginx).
    """
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"
<<<<<<< HEAD
=======

>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6

"""
Standardised Error Responses — KisanSathi
==========================================
Requirement 9: Error Handling

Provides consistent JSON error responses for all API endpoints.
Never leaves the farmer with a blank or broken screen.

Usage:
    from utils.error_responses import api_error, api_success

    return api_error("Weather data unavailable", 503, hint="Try again in a moment")
    return api_success(data, "Crop recommendation generated")

Author: Rustam Ali
"""

from __future__ import annotations
from datetime import datetime
from flask import jsonify


def api_error(message: str, status: int = 400, hint: str = "", field: str = "") -> tuple:
    """
    Return a standardised JSON error response.

    Args:
        message : human-readable error description
        status  : HTTP status code (400, 401, 403, 404, 429, 500, 503)
        hint    : optional recovery suggestion shown to user
        field   : optional field name for validation errors
    """
    body: dict = {
        "success": False,
        "error": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if hint:
        body["hint"] = hint
    if field:
        body["field"] = field

    # Map common status codes to user-friendly titles
    titles = {
        400: "Bad Request",
        401: "Authentication Required",
        403: "Access Denied",
        404: "Not Found",
        422: "Validation Error",
        429: "Too Many Requests",
        500: "Server Error",
        503: "Service Unavailable",
    }
    body["status"] = titles.get(status, "Error")

    return jsonify(body), status


def api_success(data, message: str = "Success", status: int = 200) -> tuple:
    """
    Return a standardised JSON success response.
    """
    return jsonify(
        {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    ), status


# ── Common pre-built error responses ────────────────────────────────────────


def err_missing_fields(missing: list[str]) -> tuple:
    return api_error(
        f"Missing required fields: {', '.join(missing)}",
        status=400,
        hint="Check the API documentation for required fields.",
    )


def err_invalid_value(field: str, reason: str) -> tuple:
    return api_error(
        f"Invalid value for '{field}': {reason}",
        status=422,
        field=field,
    )


def err_not_found(resource: str) -> tuple:
    return api_error(
        f"{resource} not found.",
        status=404,
        hint=f"Check that the {resource.lower()} ID or name is correct.",
    )


def err_auth_required() -> tuple:
    return api_error(
        "Authentication required.",
        status=401,
        hint="Include a valid Bearer token in the Authorization header.",
    )


def err_service_unavailable(service: str) -> tuple:
    return api_error(
        f"{service} is currently unavailable.",
        status=503,
        hint="This is a temporary issue. Please try again in a few moments.",
    )


def err_rate_limited() -> tuple:
    return api_error(
        "Too many requests.",
        status=429,
        hint="Please wait a moment before trying again.",
    )

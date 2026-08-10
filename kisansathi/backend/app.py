"""
KisanSathi — Smart Farm Decision Support System
================================================
Main application entrypoint.

Run:
    python app.py               # development
    gunicorn app:app            # production (Render / Railway)

All feature routes are defined in app_enhanced.py and imported here
so that gunicorn / deployment platforms always point to a single,
unambiguous file: app.py → app object.
"""

from app_enhanced import app, socketio  # noqa: F401
import os

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=debug,
                 allow_unsafe_werkzeug=True)

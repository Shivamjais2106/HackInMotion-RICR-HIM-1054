"""
Configuration module for KisanSathi.
All secrets are loaded from environment variables via .env file.
Never hardcode API keys or credentials here.
"""
<<<<<<< HEAD

import os

=======
import os
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
from dotenv import load_dotenv

load_dotenv()

# Weather API — set WEATHERAPI_KEY in your .env file
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY", "")

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "kisansathi")

# Flask
<<<<<<< HEAD
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        'Generate a secure value with: python -c "import secrets; print(secrets.token_hex(32))" '
        "and add it to your .env file."
    )

=======
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
<<<<<<< HEAD
=======

# All secrets loaded from .env — no hardcoded values
>>>>>>> 776251f06c852b933ff41d198cdd9be97e990da6

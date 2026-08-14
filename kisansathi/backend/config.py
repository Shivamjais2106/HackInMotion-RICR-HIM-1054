"""
Configuration module for KisanSathi.
All secrets are loaded from environment variables via .env file.
Never hardcode API keys or credentials here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Weather API — set WEATHERAPI_KEY in your .env file
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY", "")

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "kisansathi")

# Flask
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

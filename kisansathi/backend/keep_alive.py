#!/usr/bin/env python3
"""
Keep Alive Script for Render Backend
Pings the backend every 5 minutes to prevent sleep
Run this on a separate service or cron job
"""

import requests
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BACKEND_URL = "https://kisansathi-backend.onrender.com/api/health"
PING_INTERVAL = 300  # 5 minutes in seconds

def ping_backend():
    """Ping the backend to keep it alive"""
    try:
        response = requests.get(BACKEND_URL, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Backend pinged successfully at {datetime.now()}")
            return True
        else:
            logger.warning(f"⚠️ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to ping backend: {e}")
        return False

def main():
    """Main loop to keep pinging backend"""
    logger.info("🚀 Starting Keep Alive service...")
    logger.info(f"📍 Backend URL: {BACKEND_URL}")
    logger.info(f"⏱️ Ping interval: {PING_INTERVAL} seconds (5 minutes)")
    
    while True:
        try:
            ping_backend()
            time.sleep(PING_INTERVAL)
        except KeyboardInterrupt:
            logger.info("🛑 Keep Alive service stopped")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    main()

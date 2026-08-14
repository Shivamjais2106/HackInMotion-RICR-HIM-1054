"""
Database Index Setup — KisanSathi
===================================
Creates MongoDB indexes for optimal query performance.
Run once after first deployment: python db_indexes.py

Indexes created:
  users        — unique email, unique mobile
  farm_profiles — unique user_id
  health_logs  — user_id + created_at (descending)
  reminders    — crop_id + completed + scheduled_date
  messages     — group_id + timestamp
  crops        — farmer_id + status

Author: Rustam Ali
"""

from __future__ import annotations
import os
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DATABASE", "kisansathi")


def create_indexes() -> None:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGODB_DB]

    # ── users ────────────────────────────────────────────────────────────────
    db["users"].create_index("email", unique=True, sparse=True)
    db["users"].create_index("mobile", unique=True, sparse=True)
    logger.info("✅ users: email (unique), mobile (unique)")

    # ── farm_profiles ────────────────────────────────────────────────────────
    db["farm_profiles"].create_index("user_id", unique=True)
    logger.info("✅ farm_profiles: user_id (unique)")

    # ── health_logs ──────────────────────────────────────────────────────────
    db["health_logs"].create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    logger.info("✅ health_logs: (user_id, created_at DESC)")

    # ── reminders ────────────────────────────────────────────────────────────
    db["reminders"].create_index([("crop_id", ASCENDING), ("completed", ASCENDING), ("scheduled_date", ASCENDING)])
    logger.info("✅ reminders: (crop_id, completed, scheduled_date)")

    # ── crops ────────────────────────────────────────────────────────────────
    db["crops"].create_index([("farmer_id", ASCENDING), ("status", ASCENDING)])
    logger.info("✅ crops: (farmer_id, status)")

    # ── messages ─────────────────────────────────────────────────────────────
    db["messages"].create_index([("group_id", ASCENDING), ("timestamp", ASCENDING)])
    logger.info("✅ messages: (group_id, timestamp)")

    # ── groups ───────────────────────────────────────────────────────────────
    db["groups"].create_index("member_ids")
    logger.info("✅ groups: member_ids")

    logger.info("All indexes created successfully for database: %s", MONGODB_DB)
    client.close()


if __name__ == "__main__":
    create_indexes()

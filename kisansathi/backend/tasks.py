"""
Celery Background Tasks
"""

from celery_config import celery_app
from datetime import datetime, timedelta
import logging
from redis_config import get_redis
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# MongoDB Connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB = os.getenv('MONGODB_DATABASE', 'kisansathi')

try:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    db = None

# ============================================================================
# WEATHER TASKS
# ============================================================================

@celery_app.task(bind=True, max_retries=3)
def check_weather_alerts(self):
    """Check weather alerts for all users every hour"""
    try:
        logger.info("🌤️ Starting weather alert check...")
        
        if not db:
            raise Exception("Database not connected")
        
        # Get all users
        users = list(db['users'].find({}))
        
        alerts_sent = 0
        for user in users:
            location = user.get('location', '')
            if location:
                # Check weather for this location
                from utils.weather_integration import get_weather_alerts
                alerts = get_weather_alerts(location)
                
                if alerts:
                    # Store alerts in database
                    db['alerts'].insert_one({
                        'user_id': user['_id'],
                        'location': location,
                        'alerts': alerts,
                        'created_at': datetime.now().isoformat(),
                        'read': False
                    })
                    alerts_sent += 1
        
        logger.info(f"✅ Weather alerts checked. Sent {alerts_sent} alerts")
        return {'status': 'success', 'alerts_sent': alerts_sent}
    
    except Exception as exc:
        logger.error(f"❌ Weather alert check failed: {exc}")
        # Retry after 5 minutes
        raise self.retry(exc=exc, countdown=300)

# ============================================================================
# CROP REMINDER TASKS
# ============================================================================

@celery_app.task(bind=True, max_retries=3)
def send_crop_reminders(self):
    """Send daily crop reminders to users"""
    try:
        logger.info("🌾 Starting crop reminder task...")
        
        if not db:
            raise Exception("Database not connected")
        
        # Get all users
        users = list(db['users'].find({}))
        
        reminders_sent = 0
        for user in users:
            agriculture_type = user.get('agriculture_type', '')
            
            if agriculture_type:
                # Get crop calendar for today
                from utils.crop_calendar import get_crops_for_month
                from datetime import datetime
                
                current_month = datetime.now().strftime('%B')
                crops = get_crops_for_month(current_month)
                
                if crops:
                    # Store reminder
                    db['reminders'].insert_one({
                        'user_id': user['_id'],
                        'type': 'crop',
                        'crops': crops,
                        'month': current_month,
                        'created_at': datetime.now().isoformat(),
                        'sent': False
                    })
                    reminders_sent += 1
        
        logger.info(f"✅ Crop reminders sent to {reminders_sent} users")
        return {'status': 'success', 'reminders_sent': reminders_sent}
    
    except Exception as exc:
        logger.error(f"❌ Crop reminder task failed: {exc}")
        raise self.retry(exc=exc, countdown=300)

# ============================================================================
# CACHE CLEANUP TASKS
# ============================================================================

@celery_app.task(bind=True, max_retries=2)
def cleanup_cache(self):
    """Clean up old cache entries daily"""
    try:
        logger.info("🧹 Starting cache cleanup...")
        
        redis_manager = get_redis()
        if not redis_manager or not redis_manager.connected:
            logger.warning("Redis not available for cleanup")
            return {'status': 'skipped', 'reason': 'Redis not connected'}
        
        # Clear old weather cache (older than 1 hour)
        count = redis_manager.clear_pattern('cache:get_weather:*')
        logger.info(f"Cleared {count} weather cache entries")
        
        # Clear old recommendations cache
        count += redis_manager.clear_pattern('cache:get_weather_recommendations:*')
        logger.info(f"Cleared {count} recommendation cache entries")
        
        logger.info(f"✅ Cache cleanup complete. Cleared {count} entries")
        return {'status': 'success', 'entries_cleared': count}
    
    except Exception as exc:
        logger.error(f"❌ Cache cleanup failed: {exc}")
        raise self.retry(exc=exc, countdown=300)

# ============================================================================
# REPORT GENERATION TASKS
# ============================================================================

@celery_app.task(bind=True, max_retries=2)
def generate_reports(self):
    """Generate weekly reports"""
    try:
        logger.info("📊 Starting weekly report generation...")
        
        if not db:
            raise Exception("Database not connected")
        
        # Get statistics
        total_users = db['users'].count_documents({})
        total_groups = db['groups'].count_documents({})
        total_messages = db['messages'].count_documents({})
        
        # Store report
        report = {
            'type': 'weekly',
            'date': datetime.now().isoformat(),
            'statistics': {
                'total_users': total_users,
                'total_groups': total_groups,
                'total_messages': total_messages,
            }
        }
        
        db['reports'].insert_one(report)
        
        logger.info(f"✅ Weekly report generated")
        logger.info(f"   Users: {total_users}")
        logger.info(f"   Groups: {total_groups}")
        logger.info(f"   Messages: {total_messages}")
        
        return {'status': 'success', 'report': report}
    
    except Exception as exc:
        logger.error(f"❌ Report generation failed: {exc}")
        raise self.retry(exc=exc, countdown=300)

# ============================================================================
# EMAIL NOTIFICATION TASKS
# ============================================================================

@celery_app.task(bind=True, max_retries=3)
def send_email_notification(self, user_email, subject, message):
    """Send email notification to user"""
    try:
        logger.info(f"📧 Sending email to {user_email}...")
        
        # TODO: Implement email sending (using SMTP)
        # For now, just log it
        logger.info(f"Email sent: {subject}")
        
        return {'status': 'success', 'email': user_email}
    
    except Exception as exc:
        logger.error(f"❌ Email sending failed: {exc}")
        raise self.retry(exc=exc, countdown=300)

# ============================================================================
# DATA EXPORT TASKS
# ============================================================================

@celery_app.task(bind=True, max_retries=2)
def export_user_data(self, user_id):
    """Export user data as CSV/JSON"""
    try:
        logger.info(f"📥 Exporting data for user {user_id}...")
        
        if not db:
            raise Exception("Database not connected")
        
        from bson.objectid import ObjectId
        
        user = db['users'].find_one({'_id': ObjectId(user_id)})
        if not user:
            raise Exception("User not found")
        
        # Prepare export data
        export_data = {
            'user': {
                'name': user.get('name'),
                'email': user.get('email'),
                'mobile': user.get('mobile'),
                'agriculture_type': user.get('agriculture_type'),
            },
            'export_date': datetime.now().isoformat()
        }
        
        # Store export request
        db['exports'].insert_one({
            'user_id': ObjectId(user_id),
            'data': export_data,
            'created_at': datetime.now().isoformat(),
            'status': 'completed'
        })
        
        logger.info(f"✅ Data export completed for user {user_id}")
        return {'status': 'success', 'user_id': user_id}
    
    except Exception as exc:
        logger.error(f"❌ Data export failed: {exc}")
        raise self.retry(exc=exc, countdown=300)

# ============================================================================
# UTILITY TASKS
# ============================================================================

@celery_app.task
def add(x, y):
    """Simple test task"""
    logger.info(f"Adding {x} + {y}")
    return x + y

@celery_app.task
def multiply(x, y):
    """Simple test task"""
    logger.info(f"Multiplying {x} * {y}")
    return x * y

@celery_app.task
def long_running_task(duration):
    """Simulate long running task"""
    logger.info(f"Starting long running task for {duration} seconds...")
    import time
    time.sleep(duration)
    logger.info("Long running task completed")
    return {'status': 'completed', 'duration': duration}

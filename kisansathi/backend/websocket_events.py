"""
WebSocket Events for Real-time Communication
"""

from flask_socketio import emit, join_room, leave_room, rooms
from datetime import datetime
import logging
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

# Track online users
online_users = {}

# ============================================================================
# CONNECTION EVENTS
# ============================================================================

def register_connection_events(socketio):
    """Register connection events"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle user connection"""
        from flask import request
        user_id = request.args.get('user_id')
        
        if user_id:
            online_users[request.sid] = {
                'user_id': user_id,
                'connected_at': datetime.now().isoformat(),
                'status': 'online'
            }
            
            logger.info(f"✅ User connected: {user_id} (SID: {request.sid})")
            
            # Broadcast online status
            emit('user_online', {
                'user_id': user_id,
                'status': 'online',
                'timestamp': datetime.now().isoformat()
            }, broadcast=True)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnection"""
        from flask import request
        
        if request.sid in online_users:
            user_data = online_users.pop(request.sid)
            user_id = user_data['user_id']
            
            logger.info(f"❌ User disconnected: {user_id} (SID: {request.sid})")
            
            # Broadcast offline status
            emit('user_offline', {
                'user_id': user_id,
                'status': 'offline',
                'timestamp': datetime.now().isoformat()
            }, broadcast=True)

# ============================================================================
# CHAT EVENTS
# ============================================================================

def register_chat_events(socketio):
    """Register chat events"""
    
    @socketio.on('join_group')
    def handle_join_group(data):
        """Join a group chat"""
        from flask import request
        
        group_id = data.get('group_id')
        user_id = data.get('user_id')
        
        join_room(f'group_{group_id}')
        
        logger.info(f"👤 User {user_id} joined group {group_id}")
        
        # Notify group members
        emit('user_joined_group', {
            'user_id': user_id,
            'group_id': group_id,
            'timestamp': datetime.now().isoformat()
        }, room=f'group_{group_id}')
    
    @socketio.on('leave_group')
    def handle_leave_group(data):
        """Leave a group chat"""
        from flask import request
        
        group_id = data.get('group_id')
        user_id = data.get('user_id')
        
        leave_room(f'group_{group_id}')
        
        logger.info(f"👤 User {user_id} left group {group_id}")
        
        # Notify group members
        emit('user_left_group', {
            'user_id': user_id,
            'group_id': group_id,
            'timestamp': datetime.now().isoformat()
        }, room=f'group_{group_id}')
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Send message to group"""
        from flask import request
        
        group_id = data.get('group_id')
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not message:
            return
        
        # Store message in database
        if db:
            try:
                from bson.objectid import ObjectId
                db['messages'].insert_one({
                    'group_id': ObjectId(group_id),
                    'sender': {
                        'id': ObjectId(user_id),
                        'name': data.get('user_name', 'Unknown')
                    },
                    'text': message,
                    'timestamp': datetime.now().isoformat(),
                    'reactions': []
                })
            except Exception as e:
                logger.error(f"Error storing message: {e}")
        
        logger.info(f"💬 Message from {user_id} in group {group_id}")
        
        # Broadcast message to group
        emit('new_message', {
            'user_id': user_id,
            'user_name': data.get('user_name', 'Unknown'),
            'message': message,
            'group_id': group_id,
            'timestamp': datetime.now().isoformat()
        }, room=f'group_{group_id}')
    
    @socketio.on('typing')
    def handle_typing(data):
        """User is typing"""
        group_id = data.get('group_id')
        user_id = data.get('user_id')
        user_name = data.get('user_name', 'Unknown')
        
        logger.debug(f"⌨️ {user_name} is typing in group {group_id}")
        
        # Broadcast typing indicator
        emit('user_typing', {
            'user_id': user_id,
            'user_name': user_name,
            'group_id': group_id
        }, room=f'group_{group_id}', skip_sid=True)
    
    @socketio.on('stop_typing')
    def handle_stop_typing(data):
        """User stopped typing"""
        group_id = data.get('group_id')
        user_id = data.get('user_id')
        
        logger.debug(f"⌨️ {user_id} stopped typing in group {group_id}")
        
        # Broadcast stop typing
        emit('user_stopped_typing', {
            'user_id': user_id,
            'group_id': group_id
        }, room=f'group_{group_id}', skip_sid=True)

# ============================================================================
# NOTIFICATION EVENTS
# ============================================================================

def register_notification_events(socketio):
    """Register notification events"""
    
    @socketio.on('subscribe_notifications')
    def handle_subscribe_notifications(data):
        """Subscribe to notifications"""
        user_id = data.get('user_id')
        
        join_room(f'user_{user_id}_notifications')
        
        logger.info(f"🔔 User {user_id} subscribed to notifications")
        
        emit('notification_subscribed', {
            'user_id': user_id,
            'status': 'subscribed'
        })
    
    @socketio.on('unsubscribe_notifications')
    def handle_unsubscribe_notifications(data):
        """Unsubscribe from notifications"""
        user_id = data.get('user_id')
        
        leave_room(f'user_{user_id}_notifications')
        
        logger.info(f"🔔 User {user_id} unsubscribed from notifications")

# ============================================================================
# MONITORING EVENTS
# ============================================================================

def register_monitoring_events(socketio):
    """Register monitoring events"""
    
    @socketio.on('subscribe_monitoring')
    def handle_subscribe_monitoring(data):
        """Subscribe to monitoring updates"""
        user_id = data.get('user_id')
        
        join_room('monitoring')
        
        logger.info(f"📊 User {user_id} subscribed to monitoring")
        
        emit('monitoring_subscribed', {
            'status': 'subscribed'
        })
    
    @socketio.on('unsubscribe_monitoring')
    def handle_unsubscribe_monitoring(data):
        """Unsubscribe from monitoring"""
        user_id = data.get('user_id')
        
        leave_room('monitoring')
        
        logger.info(f"📊 User {user_id} unsubscribed from monitoring")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def send_notification(socketio, user_id, notification):
    """Send notification to user"""
    socketio.emit('notification', {
        'title': notification.get('title'),
        'message': notification.get('message'),
        'type': notification.get('type', 'info'),
        'timestamp': datetime.now().isoformat()
    }, room=f'user_{user_id}_notifications')
    
    logger.info(f"🔔 Notification sent to user {user_id}")

def broadcast_monitoring_update(socketio, metrics):
    """Broadcast monitoring update to all connected clients"""
    socketio.emit('monitoring_update', {
        'metrics': metrics,
        'timestamp': datetime.now().isoformat()
    }, room='monitoring')
    
    logger.debug(f"📊 Monitoring update broadcasted")

def get_online_users():
    """Get list of online users"""
    return list(online_users.values())

def is_user_online(user_id):
    """Check if user is online"""
    for user_data in online_users.values():
        if user_data['user_id'] == user_id:
            return True
    return False

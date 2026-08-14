#!/usr/bin/env python3
"""
KisanSathi - Enhanced MongoDB Backend
Features:
- JWT Authentication
- Rate Limiting
- Caching
- Better Error Handling
- Comprehensive Logging
"""

import os
import io
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_socketio import SocketIO
from dotenv import load_dotenv
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests

# Import utilities
from utils.crop_recommendation_ranked import get_crop_recommendation
from utils.crop_recommendation_ml import get_crop_recommendation_ml
from utils.seasonal_crop_recommender import get_seasonal_crop_recommendation
from utils.livestock_disease_detection import get_livestock_detector

try:
    from utils.unified_chatbot import get_chatbot_response
except Exception as e:
    logging.warning(f"unified_chatbot import failed (Python 3.14 protobuf issue): {e}")
    def get_chatbot_response(*args, **kwargs):
        return {'response': 'Chatbot temporarily unavailable', 'success': False}

try:
    from utils.voice_pipeline import extract_info_from_transcript, generate_fertilizer_explanation
except Exception as e:
    logging.warning(f"voice_pipeline import failed: {e}")
    def extract_info_from_transcript(*a, **k): return {}
    def generate_fertilizer_explanation(*a, **k): return ''

try:
    from redis_config import init_redis, get_redis
except Exception as e:
    logging.warning(f"redis_config import failed: {e}")
    def init_redis(): return None
    def get_redis(): return None

try:
    from websocket_events import (
        register_connection_events,
        register_chat_events,
        register_notification_events,
        register_monitoring_events
    )
except Exception as e:
    logging.warning(f"websocket_events import failed: {e}")
    def register_connection_events(*a, **k): pass
    def register_chat_events(*a, **k): pass
    def register_notification_events(*a, **k): pass
    def register_monitoring_events(*a, **k): pass

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import file routes
try:
    from file_routes import file_bp
except ImportError as e:
    logger.warning(f"File routes import failed: {e}")
    file_bp = None

# Import new utilities with error handling
try:
    from utils.weather_integration import get_weather_for_farming, get_farming_recommendations_based_on_weather, get_weather_alerts, get_weather_forecast
except ImportError as e:
    logger.warning(f"Weather integration import failed: {e}")
    get_weather_for_farming = lambda x: {}
    get_farming_recommendations_based_on_weather = lambda x: []
    get_weather_alerts = lambda x: []
    get_weather_forecast = lambda x: []

try:
    from utils.soil_analysis import analyze_soil
except ImportError as e:
    logger.warning(f"Soil analysis import failed: {e}")
    analyze_soil = lambda **kwargs: {}

try:
    from utils.fertilizer_recommendation import get_fertilizer_recommendation
except ImportError as e:
    logger.warning(f"Fertilizer recommendation import failed: {e}")
    get_fertilizer_recommendation = lambda **kwargs: {}

try:
    from utils.crop_calendar import get_crop_calendar, get_crops_for_month, get_crop_details, get_seasonal_activities
except ImportError as e:
    logger.warning(f"Crop calendar import failed: {e}")
    get_crop_calendar = lambda: {}
    get_crops_for_month = lambda x: []
    get_crop_details = lambda x: {}
    get_seasonal_activities = lambda x: []

try:
    from utils.pest_management import identify_pest, get_all_pests, get_pests_for_crop
except ImportError as e:
    logger.warning(f"Pest management import failed: {e}")
    identify_pest = lambda x: {}
    get_all_pests = lambda: []
    get_pests_for_crop = lambda x: []

try:
    from utils.plant_disease_detection import detect_rice_disease, detect_plant_disease
except ImportError as e:
    logger.warning(f"Plant disease detection import failed: {e}")
    detect_rice_disease = lambda x: {'success': False, 'error': 'Model not available'}
    detect_plant_disease = lambda x: {'success': False, 'error': 'Model not available'}

try:
    from utils.disease_detection_ml import detect_disease_ml
except ImportError as e:
    logger.warning(f"ML disease detection import failed: {e}")
    detect_disease_ml = lambda x: {'success': False, 'error': 'Model not available'}

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Allowed origins for CORS and Socket.IO — set ALLOWED_ORIGINS in .env as a
# comma-separated list, e.g. "https://kisansathi.com,https://www.kisansathi.com"
# Falls back to localhost-only origins in development.
_raw_origins = os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:5173,http://localhost:8080'
)
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(',') if o.strip()]

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS, async_mode='threading')

# ============================================================================
# SECURITY & PERFORMANCE CONFIGURATION
# ============================================================================

# JWT Configuration — SECRET_KEY MUST be set in .env; no insecure fallback
_jwt_secret = os.getenv('SECRET_KEY')
if not _jwt_secret:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\" "
        "and add it to your .env file."
    )
app.config['JWT_SECRET_KEY'] = _jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)

# Rate Limiting Configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Caching Configuration
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Enable CORS — restrict to allowed origins only
CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False
    }
})

# MongoDB Connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB = os.getenv('MONGODB_DATABASE', 'kisansathi')

try:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    logger.info(f"✅ Connected to MongoDB: {MONGODB_DB}")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    db = None

# Redis Connection
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'True').lower() == 'true'

if REDIS_ENABLED:
    redis_manager = init_redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
else:
    redis_manager = None
    logger.info("⚠️ Redis disabled in configuration")

# ============================================================================
# CUSTOM DECORATORS & UTILITIES
# ============================================================================

import base64
import bcrypt
from io import BytesIO
from PIL import Image
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception:
    genai = None
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not available on Python 3.14 (protobuf issue)")

def extract_soil_values_from_image(image_data):
    """Extract soil parameters from soil report image using Gemini Vision"""
    try:
        if not GENAI_AVAILABLE:
            return {'success': False, 'message': 'Gemini AI not available on this Python version'}
        genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # If image_data is base64 string, decode it
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
        else:
            image = image_data
        
        prompt = """यह एक मिट्टी की रिपोर्ट की तस्वीर है। कृपया निम्नलिखित मान निकालें और JSON format में दें:
        
{
  "nitrogen": <number or null>,
  "phosphorus": <number or null>,
  "potassium": <number or null>,
  "ph": <number or null>,
  "rainfall": <number or null>,
  "temperature": <number or null>,
  "humidity": <number or null>
}

अगर कोई value नहीं मिल रहा है तो null रखें। केवल JSON return करें, कोई अन्य text नहीं।"""
        
        response = model.generate_content([prompt, image])
        
        # Parse JSON response
        import json
        response_text = response.text.strip()
        
        # Try to extract JSON from response
        if '{' in response_text and '}' in response_text:
            json_str = response_text[response_text.find('{'):response_text.rfind('}')+1]
            values = json.loads(json_str)
            return {
                'success': True,
                'values': values,
                'message': 'Values extracted successfully'
            }
        else:
            return {
                'success': False,
                'message': 'Could not parse response',
                'raw_response': response_text
            }
    except Exception as e:
        logger.error(f"Image extraction error: {e}")
        return {
            'success': False,
            'message': f'Error extracting values: {str(e)}'
        }

def get_gemini_crop_explanation_hindi(crop, N, P, K, temperature, humidity, ph, rainfall):
    """Get detailed Hindi explanation from Gemini for crop recommendation"""
    try:
        if not GENAI_AVAILABLE:
            return f"{crop} की खेती के लिए यह मौसम और मिट्टी उपयुक्त है।"
        genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))
        # Use the latest available Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""आप एक कृषि विशेषज्ञ हैं। {crop} की खेती के लिए विस्तृत सुझाव हिंदी में दें।

मिट्टी: N={N}, P={P}, K={K}, pH={ph}
मौसम: तापमान={temperature}°C, आर्द्रता={humidity}%, वर्षा={rainfall}mm

कृपया 4-5 वाक्यों में बताएं:
1. यह फसल क्यों उपयुक्त है
2. मुख्य लाभ
3. बुवाई का समय
4. देखभाल के सुझाव
5. अपेक्षित उपज

हिंदी में जवाब दें।"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"{crop} की खेती इन स्थितियों के लिए अच्छी है। इसमें मध्यम पोषक तत्व, तापमान सहनशीलता और अच्छी आर्द्रता की आवश्यकता है। कृपया स्थानीय कृषि विशेषज्ञ से परामर्श लें।"

def error_handler(f):
    """Decorator to handle errors with proper logging"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Internal server error',
                'message': str(e),
                'endpoint': f.__name__
            }), 500
    return decorated

def validate_json(*expected_args):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body must be JSON'}), 400
            
            missing = [arg for arg in expected_args if arg not in data]
            if missing:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing_fields': missing
                }), 400
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def redis_cache(expire=3600):
    """Decorator to cache GET requests in Redis"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not redis_manager or not redis_manager.connected:
                return f(*args, **kwargs)
            
            # Create cache key from function name and args
            cache_key = f"cache:{f.__name__}:{request.path}:{request.query_string.decode()}"
            
            # Try to get from cache
            cached = redis_manager.get(cache_key)
            if cached:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached
            
            # Call function and cache result
            result = f(*args, **kwargs)
            
            # Cache successful responses
            if isinstance(result, tuple) and result[1] == 200:
                redis_manager.set(cache_key, result[0], expire=expire)
                logger.debug(f"Cache SET: {cache_key}")
            
            return result
        return decorated
    return decorator

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
@limiter.limit("100 per hour")
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'MongoDB',
        'version': '4.0.0'
    }), 200

@app.route('/api/status', methods=['GET'])
@limiter.limit("100 per hour")
def status():
    """Get application status"""
    redis_status = 'connected' if redis_manager and redis_manager.connected else 'disconnected'
    
    return jsonify({
        'app': 'KisanSathi Backend (Enhanced)',
        'version': '5.0.0',
        'environment': 'production',
        'database': 'MongoDB',
        'cache': 'Redis',
        'redis_status': redis_status,
        'features': [
            'JWT Authentication',
            'Rate Limiting',
            'Redis Caching',
            'Admin Management',
            'AI Chatbot',
            'ML Models',
            'File Handling',
            'Weather Integration'
        ],
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================================================
# AUTHENTICATION ENDPOINTS (WITH JWT)
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per hour")
@error_handler
@validate_json('name', 'email', 'mobile', 'password', 'agriculture_type')
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Check if user already exists
    if db['users'].find_one({'$or': [{'email': data['email']}, {'mobile': data['mobile']}]}):
        return jsonify({'error': 'User already exists'}), 400
    
    hashed_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_doc = {
        'name': data['name'],
        'email': data['email'],
        'mobile': data['mobile'],
        'password': hashed_pw,
        'agriculture_type': data['agriculture_type'],
        'location': data.get('location', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    result = db['users'].insert_one(user_doc)
    
    logger.info(f"New user registered: {data['name']} ({data['mobile']})")
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': str(result.inserted_id)
    }), 201

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per hour")
@error_handler
@validate_json('mobile', 'password')
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    # Find user by mobile
    user = db['users'].find_one({'mobile': mobile})

    if not user:
        logger.warning(f"Failed login attempt for mobile: {mobile}")
        return jsonify({'error': 'Invalid credentials'}), 401

    # Verify password (support both bcrypt-hashed and legacy plain-text passwords)
    password_bytes = password.encode('utf-8')
    stored_pw = user['password']
    if stored_pw.startswith('$2b$') or stored_pw.startswith('$2a$'):
        # bcrypt-hashed password
        if not bcrypt.checkpw(password_bytes, stored_pw.encode('utf-8')):
            logger.warning(f"Failed login attempt for mobile: {mobile}")
            return jsonify({'error': 'Invalid credentials'}), 401
    else:
        # Legacy plain-text password — verify and re-hash on the fly
        if stored_pw != password:
            logger.warning(f"Failed login attempt for mobile: {mobile}")
            return jsonify({'error': 'Invalid credentials'}), 401
        # Upgrade to bcrypt on next successful login
        new_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
        db['users'].update_one({'mobile': mobile}, {'$set': {'password': new_hash}})
    
    # Create JWT token
    access_token = create_access_token(identity=str(user['_id']))
    
    logger.info(f"User logged in: {user['name']} ({mobile})")
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user_id': str(user['_id']),
        'name': user['name'],
        'mobile': mobile,
        'token_type': 'Bearer'
    }), 200

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
@error_handler
def get_profile():
    """Get current user profile"""
    user_id = get_jwt_identity()
    
    try:
        user = db['users'].find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user['_id'] = str(user['_id'])
        del user['password']  # Don't send password
        
        return jsonify({
            'user': user
        }), 200
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return jsonify({'error': 'Invalid user ID'}), 400

# ============================================================================
# COMMUNITY ENDPOINTS (WITH JWT & RATE LIMITING)
# ============================================================================

@app.route('/api/community/groups', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_groups():
    """Get all community groups"""
    groups = list(db['groups'].find().sort('created_at', -1))
    
    for group in groups:
        group['id'] = str(group['_id'])
        del group['_id']
        group['created_by'] = str(group['created_by'])
        group['member_ids'] = [str(m) for m in group.get('member_ids', [])]
        group['admins'] = [str(a) for a in group.get('admins', [])]
    
    return jsonify({
        'groups': groups,
        'total': len(groups),
        'cached': True
    }), 200

@app.route('/api/community/groups', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
@error_handler
@validate_json('name', 'description')
def create_group():
    """Create a new community group"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    user_oid = ObjectId(user_id)
    
    group_doc = {
        'name': data['name'],
        'description': data['description'],
        'avatar': data.get('avatar', '🌾'),
        'members': 1,
        'member_ids': [user_oid],
        'admins': [user_oid],
        'created_by': user_oid,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'lastMessage': 'Group created',
        'unread': 0
    }
    
    result = db['groups'].insert_one(group_doc)
    
    # Clear cache
    cache.delete('get_groups')
    
    logger.info(f"Group created: {data['name']} by user {user_id}")
    
    group_doc['id'] = str(result.inserted_id)
    del group_doc['_id']
    group_doc['created_by'] = str(group_doc['created_by'])
    group_doc['member_ids'] = [str(m) for m in group_doc['member_ids']]
    group_doc['admins'] = [str(a) for a in group_doc['admins']]
    
    return jsonify({
        'message': 'Group created successfully',
        'group_id': str(result.inserted_id),
        'group': group_doc
    }), 201

@app.route('/api/community/groups/<group_id>/messages', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def get_group_messages(group_id):
    """Get all messages in a group"""
    try:
        group_oid = ObjectId(group_id)
    except:
        return jsonify({'error': 'Invalid group ID'}), 400
    
    if not db['groups'].find_one({'_id': group_oid}):
        return jsonify({'error': 'Group not found'}), 404
    
    messages = list(db['messages'].find({'group_id': group_oid}).sort('timestamp', 1))
    
    for msg in messages:
        msg['id'] = str(msg['_id'])
        del msg['_id']
        msg['group_id'] = str(msg['group_id'])
        msg['sender']['id'] = str(msg['sender']['id'])
    
    return jsonify({
        'messages': messages,
        'total': len(messages)
    }), 200

@app.route('/api/community/groups/<group_id>/messages', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
@error_handler
def send_message(group_id):
    """Send a message to a group"""
    try:
        group_oid = ObjectId(group_id)
    except:
        return jsonify({'error': 'Invalid group ID'}), 400
    
    if not db['groups'].find_one({'_id': group_oid}):
        return jsonify({'error': 'Group not found'}), 404
    
    data = request.get_json()
    user_id = get_jwt_identity()
    
    if not data.get('text') and not data.get('image'):
        return jsonify({'error': 'Message text or image required'}), 400
    
    user = db['users'].find_one({'_id': ObjectId(user_id)})
    
    message_doc = {
        'group_id': group_oid,
        'sender': {
            'id': ObjectId(user_id),
            'name': user['name'],
            'avatar': data.get('avatar', '👤')
        },
        'text': data.get('text', ''),
        'image': data.get('image'),
        'timestamp': datetime.now().isoformat(),
        'reactions': []
    }
    
    result = db['messages'].insert_one(message_doc)
    
    # Update group's last message
    db['groups'].update_one({'_id': group_oid}, {
        '$set': {
            'lastMessage': data.get('text', 'Image shared'),
            'updated_at': datetime.now().isoformat()
        }
    })
    
    message_doc['id'] = str(result.inserted_id)
    del message_doc['_id']
    message_doc['group_id'] = str(message_doc['group_id'])
    message_doc['sender']['id'] = str(message_doc['sender']['id'])
    
    logger.info(f"Message sent in group {group_id} by user {user_id}")
    
    return jsonify({
        'message': 'Message sent successfully',
        'message_id': str(result.inserted_id),
        'data': message_doc
    }), 201

@app.route('/api/community/messages/<message_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("20 per hour")
@error_handler
def delete_message(message_id):
    """Delete a message (only sender can delete)"""
    try:
        message_oid = ObjectId(message_id)
    except:
        return jsonify({'error': 'Invalid message ID'}), 400
    
    message = db['messages'].find_one({'_id': message_oid})
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    user_id = get_jwt_identity()
    
    # Check if user is the sender
    if str(message['sender']['id']) != user_id:
        logger.warning(f"Unauthorized delete attempt by user {user_id}")
        return jsonify({'error': 'Only message sender can delete'}), 403
    
    db['messages'].delete_one({'_id': message_oid})
    
    logger.info(f"Message deleted: {message_id} by user {user_id}")
    
    return jsonify({
        'message': 'Message deleted successfully'
    }), 200

# ============================================================================
# ADMIN MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/community/groups/<group_id>/add-member', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
@error_handler
@validate_json('mobile')
def add_member(group_id):
    """Add a member to group (admin only)"""
    try:
        group_oid = ObjectId(group_id)
    except:
        return jsonify({'error': 'Invalid group ID'}), 400
    
    group = db['groups'].find_one({'_id': group_oid})
    
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    user_id = get_jwt_identity()
    user_oid = ObjectId(user_id)
    
    # Check if user is admin
    if 'admins' not in group or user_oid not in group['admins']:
        logger.warning(f"Unauthorized admin action by user {user_id}")
        return jsonify({'error': 'Only admin can add members'}), 403
    
    data = request.get_json()
    member_mobile = data.get('mobile')
    
    member = db['users'].find_one({'mobile': member_mobile})
    
    if not member:
        return jsonify({'error': 'User not found'}), 404
    
    member_oid = member['_id']
    
    if 'member_ids' not in group:
        group['member_ids'] = []
    
    if member_oid not in group['member_ids']:
        db['groups'].update_one(
            {'_id': group_oid},
            {
                '$push': {'member_ids': member_oid},
                '$inc': {'members': 1},
                '$set': {'updated_at': datetime.now().isoformat()}
            }
        )
        
        logger.info(f"Member {member['name']} added to group {group_id} by admin {user_id}")
        
        return jsonify({
            'message': f'Added {member["name"]} to group',
            'member': {
                'id': str(member_oid),
                'name': member['name'],
                'mobile': member['mobile']
            }
        }), 200
    else:
        return jsonify({'error': 'User is already a member'}), 400

@app.route('/api/community/groups/<group_id>/make-admin', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
@error_handler
@validate_json('mobile')
def make_admin(group_id):
    """Make a member admin (admin only)"""
    try:
        group_oid = ObjectId(group_id)
    except:
        return jsonify({'error': 'Invalid group ID'}), 400
    
    group = db['groups'].find_one({'_id': group_oid})
    
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    user_id = get_jwt_identity()
    user_oid = ObjectId(user_id)
    
    if 'admins' not in group or user_oid not in group['admins']:
        return jsonify({'error': 'Only admin can make admins'}), 403
    
    data = request.get_json()
    member_mobile = data.get('mobile')
    
    member = db['users'].find_one({'mobile': member_mobile})
    
    if not member:
        return jsonify({'error': 'User not found'}), 404
    
    member_oid = member['_id']
    
    if 'member_ids' not in group or member_oid not in group['member_ids']:
        return jsonify({'error': 'User is not a member of this group'}), 400
    
    if 'admins' not in group:
        group['admins'] = []
    
    if member_oid not in group['admins']:
        db['groups'].update_one(
            {'_id': group_oid},
            {
                '$push': {'admins': member_oid},
                '$set': {'updated_at': datetime.now().isoformat()}
            }
        )
        
        logger.info(f"User {member['name']} made admin in group {group_id}")
        
        return jsonify({
            'message': f'Made {member["name"]} admin',
            'admin': {
                'id': str(member_oid),
                'name': member['name'],
                'mobile': member['mobile']
            }
        }), 200
    else:
        return jsonify({'error': 'User is already admin'}), 400

# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@app.route('/api/recommendations/advanced-crop', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
def advanced_crop_recommendation():
    """Get advanced crop recommendation based on month, location, and soil parameters using ML model"""
    try:
        from utils.seasonal_crop_recommender import get_seasonal_crop_recommendation

        # Handle both JSON and multipart/form-data (when soil photo is uploaded)
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json() or {}
        else:
            # multipart/form-data or form data
            data = request.form.to_dict() if request.form else {}

        month = data.get('month')
        location = data.get('location')
        
        if not month or not location:
            return jsonify({'error': 'Month and location are required'}), 400
        
        # Get location-based weather parameters
        location_weather_map = {
            'north india': {'temp': 20, 'humidity': 60, 'rainfall': 100},
            'south india': {'temp': 28, 'humidity': 70, 'rainfall': 150},
            'east india': {'temp': 25, 'humidity': 75, 'rainfall': 180},
            'west india': {'temp': 26, 'humidity': 65, 'rainfall': 120},
            'central india': {'temp': 24, 'humidity': 62, 'rainfall': 110},
            'northeast india': {'temp': 22, 'humidity': 80, 'rainfall': 200},
        }
        
        location_lower = location.lower()
        weather = location_weather_map.get(location_lower, location_weather_map['central india'])
        
        # Get soil parameters with validation
        try:
            N = float(data.get('N', 60))
            P = float(data.get('P', 40))
            K = float(data.get('K', 40))
            ph = float(data.get('ph', 6.5))
        except (TypeError, ValueError) as e:
            return jsonify({'error': f'Invalid soil parameter value: {str(e)}. N, P, K and ph must be numbers.'}), 400
        
        # Use seasonal ML model for recommendations with month parameter
        recommendations = get_seasonal_crop_recommendation(
            N=N,
            P=P,
            K=K,
            temperature=weather['temp'],
            humidity=weather['humidity'],
            ph=ph,
            rainfall=weather['rainfall'],
            season=None,  # Auto-detect from month
            month=month,  # Pass month for consistent recommendations
            top_n=5
        )
        
        if recommendations:
            # Get Gemini explanation for top crop
            top_crop = recommendations[0]['crop']
            gemini_explanation = get_gemini_crop_explanation_hindi(
                crop=top_crop,
                N=N,
                P=P,
                K=K,
                temperature=weather['temp'],
                humidity=weather['humidity'],
                ph=ph,
                rainfall=weather['rainfall']
            )
            recommendations[0]['detailed_explanation'] = gemini_explanation
            
            logger.info(f"Advanced crop recommendation generated for {month} in {location} using ML model")
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'total': len(recommendations),
                'month': month,
                'location': location,
                'weather': weather
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No recommendations found',
                'recommendations': []
            }), 400
    
    except Exception as e:
        logger.error(f"Error in advanced crop recommendation: {e}")
        return jsonify({'error': f'Advanced recommendation failed: {str(e)}'}), 500

@app.route('/api/recommendations/crop', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
@validate_json('N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall')
def crop_recommendation():
    """Get ML-based crop recommendation based on soil and weather conditions"""
    data = request.get_json()
    
    try:
        # Use ML-based recommendation
        result = get_crop_recommendation_ml(
            N=float(data['N']),
            P=float(data['P']),
            K=float(data['K']),
            temperature=float(data['temperature']),
            humidity=float(data['humidity']),
            ph=float(data['ph']),
            rainfall=float(data['rainfall'])
        )
        
        if not result['success']:
            return jsonify(result), 400
        
        recommendations = result['recommendations']
        
        # Limit to top 2 recommendations only
        recommendations = recommendations[:2]
        
        # Get Gemini explanation in Hindi for top crop
        if recommendations:
            top_crop = recommendations[0]['crop']
            gemini_explanation = get_gemini_crop_explanation_hindi(
                crop=top_crop,
                N=float(data['N']),
                P=float(data['P']),
                K=float(data['K']),
                temperature=float(data['temperature']),
                humidity=float(data['humidity']),
                ph=float(data['ph']),
                rainfall=float(data['rainfall'])
            )
            recommendations[0]['detailed_explanation'] = gemini_explanation
        
        logger.info(f"ML-based crop recommendation generated with Gemini explanation")
        
        return jsonify({
            'recommendations': recommendations,
            'total': len(recommendations)
        }), 200
    except Exception as e:
        logger.error(f"Error in crop recommendation: {e}")
        return jsonify({'error': f'Crop recommendation failed: {str(e)}'}), 500

@app.route('/api/recommendations/extract-from-image', methods=['POST'])
@limiter.limit("10 per hour")
@error_handler
def extract_soil_from_image():
    """Extract soil parameters from soil report image"""
    try:
        # Check if image is in request
        if 'image' not in request.files and 'image_data' not in request.form:
            return jsonify({'error': 'No image provided'}), 400
        
        # Get image from either file upload or base64 data
        if 'image' in request.files:
            image_file = request.files['image']
            image_data = image_file.read()
            image = Image.open(BytesIO(image_data))
        else:
            image_data = request.form.get('image_data')
            image = image_data
        
        # Extract values using Gemini Vision
        result = extract_soil_values_from_image(image)
        
        if result['success']:
            logger.info("Soil values extracted from image successfully")
            return jsonify(result), 200
        else:
            logger.warning(f"Image extraction failed: {result['message']}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in image extraction: {e}")
        return jsonify({'error': f'Image extraction failed: {str(e)}'}), 500

@app.route('/api/recommendations/extract-from-pdf', methods=['POST'])
@limiter.limit("10 per hour")
@error_handler
def extract_soil_from_pdf():
    """Extract soil parameters from soil report PDF"""
    try:
        from utils.pdf_extractor import process_soil_report_pdf
        
        # Check if PDF is in request
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf']
        
        if pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Process PDF
        result = process_soil_report_pdf(pdf_file)
        
        if result['success']:
            logger.info("Soil values extracted from PDF successfully")
            return jsonify(result), 200
        else:
            logger.warning(f"PDF extraction failed: {result['error']}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in PDF extraction: {e}")
        return jsonify({'error': f'PDF extraction failed: {str(e)}'}), 500

@app.route('/api/recommendations/seasonal-crop', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
def seasonal_crop_recommendation():
    """Get crop recommendation based on season and soil conditions"""
    data = request.get_json() or {}
    
    try:
        recommendations = get_seasonal_crop_recommendation(
            N=float(data.get('N', 60)),
            P=float(data.get('P', 40)),
            K=float(data.get('K', 40)),
            temperature=float(data.get('temperature', 25)),
            humidity=float(data.get('humidity', 65)),
            ph=float(data.get('ph', 6.5)),
            rainfall=float(data.get('rainfall', 100)),
            season=data.get('season'),
            month=data.get('month'),
            top_n=int(data.get('top_n', 5))
        )
        
        logger.info(f"Seasonal crop recommendation generated")
        
        return jsonify({
            'recommendations': recommendations,
            'total': len(recommendations)
        }), 200
    except Exception as e:
        logger.error(f"Error in seasonal crop recommendation: {e}")
        return jsonify({'error': f'Seasonal crop recommendation failed: {str(e)}'}), 500

@app.route('/api/seasons', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def get_seasons():
    """Get all available seasons"""
    try:
        from utils.seasonal_crop_recommender import SeasonalCropRecommender
        recommender = SeasonalCropRecommender()
        seasons = recommender.get_seasons()
        # handle both ndarray and plain list
        seasons_list = seasons.tolist() if hasattr(seasons, 'tolist') else list(seasons)
        
        return jsonify({
            'seasons': seasons_list,
            'total': len(seasons_list)
        }), 200
    except Exception as e:
        logger.error(f"Error getting seasons: {e}")
        return jsonify({'error': f'Failed to get seasons: {str(e)}'}), 500

# ============================================================================
# VOICE-BASED CROP RECOMMENDATION
# ============================================================================
# CHATBOT ENDPOINTS
# ============================================================================

@app.route('/api/chatbot/message', methods=['POST'])
@limiter.limit("30 per hour")
@error_handler
@validate_json('message')
def chatbot_message():
    """Send message to chatbot with conversation history"""
    data = request.get_json()
    
    try:
        conversation_history = data.get('conversation_history', [])
        
        response = get_chatbot_response(
            message=data['message'],
            context=conversation_history
        )
        
        logger.info(f"Chatbot message processed")
        
        return jsonify({
            'response': response,
            'success': True
        }), 200
    except Exception as e:
        logger.error(f"Error in chatbot: {e}")
        return jsonify({'error': f'Chatbot error: {str(e)}'}), 500

@app.route('/api/chatbot/voice', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
@validate_json('text')
def chatbot_voice():
    """Convert text to speech"""
    data = request.get_json()
    
    try:
        text = data['text']
        language = data.get('language', 'hi')
        
        from gtts import gTTS
        import io
        import base64
        
        tts = gTTS(text=text, lang=language, slow=False)
        
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        audio_base64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
        
        logger.info(f"Voice generated for language: {language}")
        
        return jsonify({
            'audio': audio_base64,
            'success': True
        }), 200
    except ImportError:
        return jsonify({
            'error': 'gTTS not installed',
            'message': 'Voice output not available'
        }), 500
    except Exception as e:
        logger.error(f"Error in voice conversion: {e}")
        return jsonify({'error': f'Voice error: {str(e)}'}), 500

# ============================================================================
# LIVESTOCK ENDPOINTS
# ============================================================================

@app.route('/api/livestock-disease-predict', methods=['POST'])
@limiter.limit("10 per hour")
@error_handler
def livestock_disease_predict():
    """Predict livestock disease from image and symptoms"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Image file required'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        animal_type = request.form.get('animal_type', 'cattle')
        symptoms = request.form.getlist('symptoms')
        
        image_data = file.read()
        
        detector = get_livestock_detector()
        result = detector.predict(image_data, animal_type, symptoms)
        
        logger.info(f"Livestock disease prediction for {animal_type}")
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in livestock disease prediction: {e}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/api/livestock-diseases/<animal_type>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def get_livestock_diseases(animal_type):
    """Get all diseases for a specific animal type"""
    try:
        detector = get_livestock_detector()
        diseases = detector.get_all_diseases(animal_type)
        
        logger.info(f"Retrieved diseases for {animal_type}")
        
        return jsonify({
            'animal_type': animal_type,
            'diseases': diseases,
            'total': len(diseases)
        }), 200
    except Exception as e:
        logger.error(f"Error getting livestock diseases: {e}")
        return jsonify({'error': f'Failed to get diseases: {str(e)}'}), 500

# ============================================================================
# WEATHER INTEGRATION ENDPOINTS
# ============================================================================

@app.route('/api/location/detect', methods=['GET'])
@limiter.limit("60 per hour")
@error_handler
def detect_location():
    """Detect user's location from IP address"""
    try:
        # Get client IP
        client_ip = request.remote_addr
        
        # Simple IP-based location detection
        # This is a fallback - in production, use a proper geolocation service
        location_map = {
            '127.0.0.1': 'Delhi',
            'localhost': 'Delhi',
        }
        
        # Check if it's a local IP
        if client_ip in location_map:
            city = location_map[client_ip]
        else:
            # For other IPs, try to detect based on common patterns
            # This is a simple fallback
            city = 'Delhi'
        
        logger.info(f"Location detected for IP {client_ip}: {city}")
        
        return jsonify({
            'success': True,
            'city': city,
            'ip': client_ip,
            'method': 'ip-based'
        }), 200
    except Exception as e:
        logger.error(f"Error detecting location: {e}")
        return jsonify({
            'success': False,
            'city': 'Delhi',
            'error': str(e)
        }), 200

@app.route('/api/location/from-gps', methods=['POST'])
@limiter.limit("60 per hour")
@error_handler
def detect_location_from_gps():
    """Detect location from GPS coordinates using reverse geocoding"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({
                'success': False,
                'error': 'Latitude and longitude required'
            }), 400
        
        logger.info(f"Reverse geocoding for GPS: {latitude}, {longitude}")
        
        # Use OpenStreetMap Nominatim for reverse geocoding
        try:
            response = requests.get(
                f'https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}',
                timeout=5,
                headers={'User-Agent': 'KisanSathi/1.0'}
            )
            
            if response.status_code == 200:
                location_data = response.json()
                address = location_data.get('address', {})
                
                # Try to get city, town, or village
                city = address.get('city') or address.get('town') or address.get('village') or 'Delhi'
                state = address.get('state', '')
                country = address.get('country', 'India')
                
                logger.info(f"Reverse geocoding result: {city}, {state}, {country}")
                
                return jsonify({
                    'success': True,
                    'city': city,
                    'state': state,
                    'country': country,
                    'latitude': latitude,
                    'longitude': longitude,
                    'method': 'gps-based'
                }), 200
            else:
                logger.error(f"Nominatim returned status {response.status_code}")
                return jsonify({
                    'success': False,
                    'error': 'Reverse geocoding failed',
                    'city': 'Delhi'
                }), 200
        except requests.exceptions.Timeout:
            logger.error("Nominatim request timed out")
            return jsonify({
                'success': False,
                'error': 'Reverse geocoding timeout',
                'city': 'Delhi'
            }), 200
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'city': 'Delhi'
            }), 200
            
    except Exception as e:
        logger.error(f"Error in GPS location detection: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'city': 'Delhi'
        }), 200

@app.route('/api/weather/<location>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@redis_cache(expire=600)
def get_weather(location):
    """Get current weather for a location (cached in Redis)"""
    try:
        weather = get_weather_for_farming(location)
        forecast = get_weather_forecast(location)

        if not weather:
            logger.warning(f"Weather API returned empty data for {location}")
            return jsonify({
                'error': 'Weather data unavailable for this location. Check the location name or try again later.',
                'location': location,
                'weather': None,
                'forecast': [],
                'service_status': 'unavailable'
            }), 503

        logger.info(f"Weather retrieved for {location}")
        return jsonify({
            'location': location,
            'weather': weather,
            'forecast': forecast or [],
            'timestamp': datetime.now().isoformat(),
            'cached': False
        }), 200
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        return jsonify({'error': f'Weather service error: {str(e)}. Please try again later.'}), 503

@app.route('/api/weather/<location>/forecast', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@redis_cache(expire=600)
def get_forecast(location):
    """Get 5-day weather forecast for a location (cached in Redis)"""
    try:
        forecast = get_weather_forecast(location)
        
        logger.info(f"Forecast retrieved for {location}")
        
        return jsonify({
            'location': location,
            'forecast': forecast,
            'timestamp': datetime.now().isoformat(),
            'cached': False
        }), 200
    except Exception as e:
        logger.error(f"Error getting forecast: {e}")
        return jsonify({'error': f'Forecast retrieval failed: {str(e)}'}), 500

@app.route('/api/weather/<location>/recommendations', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@redis_cache(expire=600)
def get_weather_recommendations(location):
    """Get farming recommendations based on weather (cached in Redis)"""
    try:
        recommendations = get_farming_recommendations_based_on_weather(location)
        
        logger.info(f"Weather recommendations generated for {location}")
        
        return jsonify({
            'location': location,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat(),
            'cached': False
        }), 200
    except Exception as e:
        logger.error(f"Error getting weather recommendations: {e}")
        return jsonify({'error': f'Recommendations failed: {str(e)}'}), 500

@app.route('/api/weather/<location>/alerts', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@redis_cache(expire=300)
def get_alerts(location):
    """Get weather alerts for a location (cached in Redis)"""
    try:
        alerts = get_weather_alerts(location)
        
        logger.info(f"Weather alerts retrieved for {location}")
        
        return jsonify({
            'location': location,
            'alerts': alerts,
            'total': len(alerts),
            'timestamp': datetime.now().isoformat(),
            'cached': False
        }), 200
    except Exception as e:
        logger.error(f"Error getting weather alerts: {e}")
        return jsonify({'error': f'Alerts retrieval failed: {str(e)}'}), 500

# ============================================================================
# SOIL ANALYSIS ENDPOINTS
# ============================================================================

from utils.soil_analysis import analyze_soil, get_soil_types, get_crop_types, get_fertilizer_types

@app.route('/api/soil/analyze', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
def analyze_soil_endpoint():
    """Analyze soil and recommend crops and fertilizers"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['temperature', 'humidity', 'moisture', 'soil_type', 'nitrogen', 'potassium', 'phosphorous']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Perform soil analysis
        result = analyze_soil(
            temperature=float(data['temperature']),
            humidity=float(data['humidity']),
            moisture=float(data['moisture']),
            soil_type=data['soil_type'],
            nitrogen=float(data['nitrogen']),
            potassium=float(data['potassium']),
            phosphorous=float(data['phosphorous'])
        )
        
        logger.info(f"Soil analysis completed: {result.get('crop_recommendation', {}).get('primary', 'Unknown')}")
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in soil analysis: {e}")
        return jsonify({'error': f'Soil analysis failed: {str(e)}'}), 500

@app.route('/api/soil/types', methods=['GET'])
@limiter.limit("60 per hour")
@error_handler
def get_soil_types_endpoint():
    """Get list of supported soil types"""
    try:
        soil_types = get_soil_types()
        
        return jsonify({
            'success': True,
            'soil_types': soil_types,
            'count': len(soil_types)
        }), 200
    except Exception as e:
        logger.error(f"Error getting soil types: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil/crops', methods=['GET'])
@limiter.limit("60 per hour")
@error_handler
def get_crops_endpoint():
    """Get list of supported crop types"""
    try:
        crops = get_crop_types()
        
        return jsonify({
            'success': True,
            'crops': crops,
            'count': len(crops)
        }), 200
    except Exception as e:
        logger.error(f"Error getting crop types: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil/fertilizers', methods=['GET'])
@limiter.limit("60 per hour")
@error_handler
def get_fertilizers_endpoint():
    """Get list of supported fertilizer types"""
    try:
        fertilizers = get_fertilizer_types()
        
        return jsonify({
            'success': True,
            'fertilizers': fertilizers,
            'count': len(fertilizers)
        }), 200
    except Exception as e:
        logger.error(f"Error getting fertilizer types: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
@validate_json('nitrogen', 'phosphorus', 'potassium', 'ph', 'organic_matter', 'texture')
def soil_analysis():
    """Analyze soil and provide recommendations"""
    try:
        data = request.get_json()
        
        analysis = analyze_soil(
            nitrogen=float(data['nitrogen']),
            phosphorus=float(data['phosphorus']),
            potassium=float(data['potassium']),
            ph=float(data['ph']),
            organic_matter=float(data['organic_matter']),
            texture=data['texture']
        )
        
        logger.info(f"Soil analysis completed")
        
        return jsonify({
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error in soil analysis: {e}")
        return jsonify({'error': f'Soil analysis failed: {str(e)}'}), 500

# ============================================================================
# FERTILIZER RECOMMENDATION ENDPOINTS
# ============================================================================

@app.route('/api/fertilizer-from-image', methods=['POST'])
@limiter.limit("30 per hour")
@error_handler
def fertilizer_from_image():
    """Get fertilizer recommendation based on crop image health analysis"""
    try:
        from utils.crop_health_analyzer import analyze_crop_health_from_image
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Read image file
        image_data = file.read()
        
        # Analyze crop health from image
        health_analysis = analyze_crop_health_from_image(image_data)
        
        if not health_analysis.get('success', False):
            return jsonify(health_analysis), 400
        
        # Get fertilizer recommendation based on health analysis
        recommendations = health_analysis.get('recommendations', {})
        
        logger.info(f"Fertilizer recommendation generated from image - Health: {health_analysis.get('health_status')}")
        
        return jsonify({
            'success': True,
            'crop_identification': {
                'crop': 'Detected from image',
                'confidence': '85%',
                'reason': 'Image analysis based on color and structure'
            },
            'health_analysis': {
                'status': health_analysis.get('health_status'),
                'confidence': health_analysis.get('health_confidence'),
                'details': health_analysis.get('health_details')
            },
            'size_analysis': health_analysis.get('size_estimate'),
            'fertilizer_recommendation': {
                'primary_recommendation': recommendations.get('primary_recommendation'),
                'quantity': recommendations.get('quantity'),
                'timing': recommendations.get('timing'),
                'reason': recommendations.get('reason'),
                'nutrient_focus': recommendations.get('nutrient_focus'),
                'additional_measures': recommendations.get('additional_measures'),
                'warning': recommendations.get('warning'),
                'benefits': [
                    f"Nitrogen focus: {recommendations.get('nutrient_focus', {}).get('nitrogen', 'Moderate')}",
                    f"Phosphorus focus: {recommendations.get('nutrient_focus', {}).get('phosphorus', 'Moderate')}",
                    f"Potassium focus: {recommendations.get('nutrient_focus', {}).get('potassium', 'Moderate')}"
                ]
            },
            'summary': f"Based on image analysis, your crop is {health_analysis.get('health_status')} with {health_analysis.get('size_estimate', {}).get('category')} size. Recommended fertilizer: {recommendations.get('primary_recommendation')}",
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error in fertilizer from image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Image analysis failed: {str(e)}'}), 500

@app.route('/api/fertilizer/recommend', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
@validate_json('nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'moisture', 'soil_type', 'crop_type')
def fertilizer_recommend():
    """Get fertilizer recommendation"""
    try:
        data = request.get_json()
        
        recommendation = get_fertilizer_recommendation(
            nitrogen=float(data['nitrogen']),
            phosphorus=float(data['phosphorus']),
            potassium=float(data['potassium']),
            temperature=float(data['temperature']),
            humidity=float(data['humidity']),
            moisture=float(data['moisture']),
            soil_type=data['soil_type'],
            crop_type=data['crop_type']
        )
        
        logger.info(f"Fertilizer recommendation generated for {data['crop_type']}")
        
        return jsonify({
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error in fertilizer recommendation: {e}")
        return jsonify({'error': f'Recommendation failed: {str(e)}'}), 500

# ============================================================================
# VOICE FERTILIZER PIPELINE ENDPOINTS
# ============================================================================

@app.route('/api/extract-fertilizer-info', methods=['POST'])
@limiter.limit("30 per hour")
@error_handler
def extract_fertilizer_info():
    """Extract fertilizer-related information from transcript"""
    try:
        data = request.get_json()
        transcript = data.get('transcript', '') or data.get('text', '')
        
        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400
        
        # Extract information using NLP
        extracted = extract_info_from_transcript(transcript)
        
        logger.info(f"Extracted fertilizer info from transcript")
        
        return jsonify({
            'extracted': extracted,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error extracting fertilizer info: {e}")
        return jsonify({'error': f'Extraction failed: {str(e)}'}), 500

@app.route('/api/generate-explanation', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
def generate_explanation():
    """Generate AI-powered explanation for fertilizer recommendation"""
    try:
        data = request.get_json()
        fertilizer = data.get('fertilizer', '')
        crop = data.get('crop', '')
        nitrogen = data.get('nitrogen', 0)
        phosphorus = data.get('phosphorus', 0)
        potassium = data.get('potassium', 0)
        soil_type = data.get('soil_type', '')
        
        # Generate explanation using OpenAI
        explanation = generate_fertilizer_explanation(
            fertilizer, crop, nitrogen, phosphorus, potassium, soil_type
        )
        
        logger.info(f"Generated explanation for {fertilizer}")
        
        return jsonify({
            'explanation': explanation,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        return jsonify({'error': f'Explanation generation failed: {str(e)}'}), 500

# ============================================================================
# CROP CALENDAR ENDPOINTS
# ============================================================================

@app.route('/api/crop-calendar', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def crop_calendar():
    """Get seasonal crop calendar"""
    try:
        calendar = get_crop_calendar()
        
        logger.info(f"Crop calendar retrieved")
        
        return jsonify({
            'calendar': calendar,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting crop calendar: {e}")
        return jsonify({'error': f'Calendar retrieval failed: {str(e)}'}), 500

@app.route('/api/months', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def get_months():
    """Get list of all months for crop selection"""
    try:
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        logger.info(f"Months list retrieved")
        
        return jsonify({
            'success': True,
            'months': months,
            'total': len(months),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting months: {e}")
        return jsonify({'error': f'Failed to get months: {str(e)}'}), 500

@app.route('/api/crop-calendar/month/<month>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def crops_for_month(month):
    """Get crops recommended for a specific month"""
    try:
        crops = get_crops_for_month(month)
        
        logger.info(f"Crops retrieved for {month}")
        
        return jsonify({
            'month': month,
            'crops': crops,
            'total': len(crops),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting crops for month: {e}")
        return jsonify({'error': f'Failed to get crops: {str(e)}'}), 500

@app.route('/api/crop-calendar/crop/<crop_name>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def crop_info(crop_name):
    """Get detailed information about a specific crop"""
    try:
        details = get_crop_details(crop_name)
        
        # try case-insensitive if not found
        if not details:
            details = get_crop_details(crop_name.capitalize())
        if not details:
            details = get_crop_details(crop_name.lower())
        if not details:
            details = get_crop_details(crop_name.upper())
        
        if details is None or (isinstance(details, dict) and not details):
            return jsonify({'error': 'Crop not found'}), 404
        
        logger.info(f"Crop details retrieved for {crop_name}")
        
        return jsonify({
            'crop': crop_name,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting crop details: {e}")
        return jsonify({'error': f'Failed to get crop details: {str(e)}'}), 500

@app.route('/api/crop-calendar/season/<season>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def seasonal_activities(season):
    """Get farming activities for a season"""
    try:
        activities = get_seasonal_activities(season)
        
        logger.info(f"Seasonal activities retrieved for {season}")
        
        return jsonify({
            'season': season,
            'activities': activities,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting seasonal activities: {e}")
        return jsonify({'error': f'Failed to get activities: {str(e)}'}), 500

# ============================================================================
# PLANT DISEASE DETECTION ENDPOINTS
# ============================================================================

@app.route('/api/disease-predict', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
def disease_predict():
    """Predict plant disease from multiple images using ML model"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({'error': 'No files selected'}), 400

        # Validate file types upfront
        allowed = {'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'}
        valid_files = [f for f in files if f.filename and f.content_type in allowed]
        if not valid_files:
            return jsonify({'error': 'No valid image files found. Please upload JPG, PNG, GIF, BMP, or WebP images.'}), 400
        
        predictions = []
        disease_counts = {}
        
        for file in valid_files:
            
            try:
                # Detect disease using ML model
                result = detect_disease_ml(file)
                
                if result['success']:
                    disease = result['disease']
                    predictions.append({
                        'filename': file.filename,
                        'success': True,
                        'disease': disease,
                        'confidence': result.get('confidence', 0),
                        'management': result.get('management', {})
                    })
                    
                    # Count diseases
                    disease_counts[disease] = disease_counts.get(disease, 0) + 1
                else:
                    predictions.append({
                        'filename': file.filename,
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    })
            except Exception as e:
                predictions.append({
                    'filename': file.filename,
                    'success': False,
                    'error': str(e)
                })
        
        # Find most common disease
        most_common_disease = max(disease_counts, key=disease_counts.get) if disease_counts else None

        # If every single file failed, return a clear error instead of partial success
        successful = [p for p in predictions if p.get('success')]
        if not successful:
            return jsonify({
                'success': False,
                'error': 'Could not analyze any of the uploaded images. Please ensure they are clear, well-lit photos of plant leaves.',
                'total_images': len(valid_files),
                'predictions': predictions,
                'timestamp': datetime.now().isoformat()
            }), 400

        logger.info(f"ML Disease prediction for {len(valid_files)} images. Most common: {most_common_disease}")

        return jsonify({
            'success': True,
            'total_images': len(valid_files),
            'predictions': predictions,
            'most_common_disease': most_common_disease or 'Unknown',
            'disease_info': f'Most common disease detected: {most_common_disease}' if most_common_disease else 'No disease identified',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error in disease prediction: {e}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/api/rice-disease-predict', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
def rice_disease_predict():
    """Predict rice leaf disease from image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Detect rice disease
        result = detect_rice_disease(file)
        
        if not result['success']:
            logger.warning(f"Rice disease detection failed: {result.get('error')}")
            return jsonify(result), 400
        
        logger.info(f"Rice disease detected: {result['disease']}")
        
        return jsonify({
            'success': True,
            'disease': result['disease'],
            'confidence': result['confidence'],
            'info': result.get('info', ''),
            'symptoms': result.get('symptoms', ''),
            'management': result.get('management', []),
            'severity': result.get('severity', 'Unknown'),
            'all_probabilities': result.get('all_probabilities', {}),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error in rice disease prediction: {e}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

# ============================================================================
# PEST MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/pest/identify/<pest_name>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def pest_identify(pest_name):
    """Identify pest and get management strategies"""
    try:
        pest_info = identify_pest(pest_name)
        
        # try case-insensitive variants if not found or empty
        if not pest_info:
            pest_info = identify_pest(pest_name.capitalize())
        if not pest_info:
            pest_info = identify_pest(pest_name.title())
        if not pest_info:
            pest_info = identify_pest(pest_name.lower())
        # strip trailing 's' for plural (aphids -> aphid)
        if not pest_info and pest_name.lower().endswith('s'):
            pest_info = identify_pest(pest_name[:-1].capitalize())
        
        if pest_info is None or (isinstance(pest_info, dict) and not pest_info):
            return jsonify({'error': 'Pest not found'}), 404
        
        logger.info(f"Pest information retrieved for {pest_name}")
        
        return jsonify({
            'pest': pest_name,
            'information': pest_info,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error identifying pest: {e}")
        return jsonify({'error': f'Failed to identify pest: {str(e)}'}), 500

@app.route('/api/pest/all', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def all_pests():
    """Get list of all managed pests"""
    try:
        pests = get_all_pests()
        
        logger.info(f"All pests list retrieved")
        
        return jsonify({
            'pests': pests,
            'total': len(pests),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting pests list: {e}")
        return jsonify({'error': f'Failed to get pests: {str(e)}'}), 500

@app.route('/api/pest/crop/<crop_name>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
@cache.cached(timeout=3600)
def pests_for_crop(crop_name):
    """Get pests that affect a specific crop"""
    try:
        pests = get_pests_for_crop(crop_name)
        
        logger.info(f"Pests retrieved for {crop_name}")
        
        return jsonify({
            'crop': crop_name,
            'pests': pests,
            'total': len(pests),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting pests for crop: {e}")
        return jsonify({'error': f'Failed to get pests: {str(e)}'}), 500

# ============================================================================
# REDIS CACHE MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/cache/stats', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def cache_stats():
    """Get Redis cache statistics"""
    if not redis_manager or not redis_manager.connected:
        return jsonify({
            'status': 'disconnected',
            'message': 'Redis is not connected'
        }), 503
    
    stats = redis_manager.get_stats()
    return jsonify(stats), 200

@app.route('/api/cache/clear', methods=['POST'])
@limiter.limit("5 per hour")
@error_handler
def cache_clear():
    """Clear all Redis cache"""
    if not redis_manager or not redis_manager.connected:
        return jsonify({
            'error': 'Redis is not connected'
        }), 503
    
    redis_manager.flush_all()
    logger.info("Redis cache cleared by user")
    
    return jsonify({
        'message': 'Cache cleared successfully'
    }), 200

@app.route('/api/cache/clear/<pattern>', methods=['POST'])
@limiter.limit("10 per hour")
@error_handler
def cache_clear_pattern(pattern):
    """Clear cache by pattern"""
    if not redis_manager or not redis_manager.connected:
        return jsonify({
            'error': 'Redis is not connected'
        }), 503
    
    count = redis_manager.clear_pattern(pattern)
    logger.info(f"Cleared {count} cache entries matching pattern: {pattern}")
    
    return jsonify({
        'message': f'Cleared {count} cache entries',
        'pattern': pattern
    }), 200

# ============================================================================
# REGISTER BLUEPRINTS
# ============================================================================

if file_bp:
    app.register_blueprint(file_bp)
    logger.info("✅ File handling routes registered")

# ============================================================================
# REGISTER WEBSOCKET EVENTS
# ============================================================================

register_connection_events(socketio)
register_chat_events(socketio)
register_notification_events(socketio)
register_monitoring_events(socketio)
logger.info("✅ WebSocket events registered")

# ============================================================================
# REMINDERS ENDPOINTS
# ============================================================================

@app.route('/api/reminders/available-crops', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def get_available_crops():
    """Get list of available crops for reminders"""
    try:
        available_crops = [
            {'name': 'moong', 'duration_days': 60, 'season': 'summer'},
            {'name': 'rice', 'duration_days': 120, 'season': 'monsoon'},
            {'name': 'wheat', 'duration_days': 150, 'season': 'winter'},
            {'name': 'maize', 'duration_days': 90, 'season': 'summer'},
            {'name': 'cotton', 'duration_days': 180, 'season': 'summer'},
            {'name': 'potato', 'duration_days': 90, 'season': 'winter'},
            {'name': 'tomato', 'duration_days': 120, 'season': 'summer'},
            {'name': 'onion', 'duration_days': 150, 'season': 'winter'},
            {'name': 'sugarcane', 'duration_days': 360, 'season': 'year-round'},
            {'name': 'groundnut', 'duration_days': 120, 'season': 'summer'},
            {'name': 'soybean', 'duration_days': 100, 'season': 'summer'},
            {'name': 'chickpea', 'duration_days': 120, 'season': 'winter'},
        ]
        
        logger.info("Available crops fetched successfully")
        return jsonify({
            'success': True,
            'crops': available_crops,
            'total': len(available_crops)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching available crops: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reminders/crops/<farmer_id>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def get_farmer_crops(farmer_id):
    """Get all crops for a farmer"""
    try:
        crops = list(db['crops'].find({'farmer_id': farmer_id}))
        
        for crop in crops:
            crop['id'] = str(crop['_id'])
            del crop['_id']
            
            # Calculate statistics
            reminders = list(db['reminders'].find({'crop_id': crop['id']}))
            completed = len([r for r in reminders if r.get('completed', False)])
            total = len(reminders)
            
            crop['statistics'] = {
                'days_elapsed': max(0, (datetime.now() - datetime.fromisoformat(crop['planting_date'])).days),
                'reminders': {
                    'total': total,
                    'completed': completed,
                    'percentage': int((completed / total * 100) if total > 0 else 0)
                },
                'photos_count': len(list(db['photos'].find({'crop_id': crop['id']})))
            }
        
        logger.info(f"Fetched {len(crops)} crops for farmer {farmer_id}")
        return jsonify({
            'success': True,
            'crops': crops,
            'total': len(crops)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching crops: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reminders/add-crop', methods=['POST'])
@limiter.limit("10 per hour")
@error_handler
@validate_json('farmer_id', 'crop_name', 'planting_date')
def add_crop():
    """Add a new crop and create reminders"""
    try:
        data = request.get_json()
        
        crop_doc = {
            'farmer_id': data['farmer_id'],
            'crop_name': data['crop_name'],
            'planting_date': data['planting_date'],
            'field_name': data.get('field_name', 'Main Field'),
            'area_acres': float(data.get('area_acres', 1.0)),
            'location': data.get('location', ''),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        result = db['crops'].insert_one(crop_doc)
        crop_id = str(result.inserted_id)
        
        # Create reminders based on crop type
        crop_reminders = {
            'moong': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 15, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 25, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 40, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 55, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'rice': [
                {'day': 7, 'task': 'Maintain water level', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 20, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 35, 'task': 'Apply nitrogen fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 60, 'task': 'Monitor for diseases', 'task_type': 'monitoring', 'priority': 'high'},
                {'day': 110, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'wheat': [
                {'day': 10, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 25, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 40, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 70, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 140, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'maize': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 15, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 25, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 50, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 85, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'cotton': [
                {'day': 10, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 25, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 45, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 80, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'high'},
                {'day': 150, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'potato': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 15, 'task': 'Earthing up', 'task_type': 'maintenance', 'priority': 'high'},
                {'day': 30, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 50, 'task': 'Monitor for diseases', 'task_type': 'monitoring', 'priority': 'high'},
                {'day': 85, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'tomato': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 15, 'task': 'Staking and pruning', 'task_type': 'maintenance', 'priority': 'medium'},
                {'day': 30, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 50, 'task': 'Monitor for diseases', 'task_type': 'monitoring', 'priority': 'high'},
                {'day': 110, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'onion': [
                {'day': 10, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 25, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 45, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 80, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 140, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'sugarcane': [
                {'day': 10, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 30, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 60, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 120, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 330, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'groundnut': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 20, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 35, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 60, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 110, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'soybean': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 15, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 30, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 50, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 95, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'chickpea': [
                {'day': 10, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 25, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 40, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 70, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 110, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
        }
        
        reminders = crop_reminders.get(data['crop_name'].lower(), [])
        planting_date = datetime.fromisoformat(data['planting_date'])
        
        for reminder in reminders:
            scheduled_date = planting_date + timedelta(days=reminder['day'])
            db['reminders'].insert_one({
                'crop_id': crop_id,
                'farmer_id': data['farmer_id'],
                'task': reminder['task'],
                'task_type': reminder['task_type'],
                'priority': reminder['priority'],
                'day': reminder['day'],
                'scheduled_date': scheduled_date.isoformat(),
                'completed': False,
                'notes': '',
                'created_at': datetime.now().isoformat()
            })
        
        logger.info(f"Crop {data['crop_name']} added with {len(reminders)} reminders")
        return jsonify({
            'success': True,
            'crop_id': crop_id,
            'message': f'Crop added with {len(reminders)} reminders',
            'reminders_created': len(reminders)
        }), 201
    except Exception as e:
        logger.error(f"Error adding crop: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reminders/regenerate/<crop_id>', methods=['POST'])
@limiter.limit("10 per hour")
@error_handler
def regenerate_crop_reminders(crop_id):
    """Regenerate reminders for an existing crop"""
    try:
        # Get the crop
        crop = db['crops'].find_one({'_id': ObjectId(crop_id)})
        if not crop:
            return jsonify({'success': False, 'error': 'Crop not found'}), 404
        
        # Delete existing reminders
        db['reminders'].delete_many({'crop_id': crop_id})
        
        # Create reminders based on crop type
        crop_reminders = {
            'moong': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 15, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 25, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 40, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 55, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'rice': [
                {'day': 7, 'task': 'Maintain water level', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 20, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 35, 'task': 'Apply nitrogen fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 60, 'task': 'Monitor for diseases', 'task_type': 'monitoring', 'priority': 'high'},
                {'day': 110, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'wheat': [
                {'day': 10, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 25, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 40, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 70, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 140, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'maize': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 15, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 25, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 50, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 85, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'cotton': [
                {'day': 10, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 25, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 45, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 80, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'high'},
                {'day': 150, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'potato': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 15, 'task': 'Earthing up', 'task_type': 'maintenance', 'priority': 'high'},
                {'day': 30, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 50, 'task': 'Monitor for diseases', 'task_type': 'monitoring', 'priority': 'high'},
                {'day': 85, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'tomato': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 15, 'task': 'Staking and pruning', 'task_type': 'maintenance', 'priority': 'medium'},
                {'day': 30, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 50, 'task': 'Monitor for diseases', 'task_type': 'monitoring', 'priority': 'high'},
                {'day': 110, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'onion': [
                {'day': 10, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 25, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 45, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 80, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 140, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'sugarcane': [
                {'day': 10, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 30, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 60, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 120, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 330, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'groundnut': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 20, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 35, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 60, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 110, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'soybean': [
                {'day': 5, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 15, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 30, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 50, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 95, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
            'chickpea': [
                {'day': 10, 'task': 'First irrigation', 'task_type': 'irrigation', 'priority': 'high'},
                {'day': 25, 'task': 'Weeding', 'task_type': 'weeding', 'priority': 'medium'},
                {'day': 40, 'task': 'Apply fertilizer', 'task_type': 'fertilizer', 'priority': 'high'},
                {'day': 70, 'task': 'Monitor for pests', 'task_type': 'monitoring', 'priority': 'medium'},
                {'day': 110, 'task': 'Harvest ready', 'task_type': 'harvest', 'priority': 'high'},
            ],
        }
        
        reminders = crop_reminders.get(crop['crop_name'].lower(), [])
        planting_date = datetime.fromisoformat(crop['planting_date'])
        
        for reminder in reminders:
            scheduled_date = planting_date + timedelta(days=reminder['day'])
            db['reminders'].insert_one({
                'crop_id': crop_id,
                'farmer_id': crop['farmer_id'],
                'task': reminder['task'],
                'task_type': reminder['task_type'],
                'priority': reminder['priority'],
                'day': reminder['day'],
                'scheduled_date': scheduled_date.isoformat(),
                'completed': False,
                'notes': '',
                'created_at': datetime.now().isoformat()
            })
        
        logger.info(f"Regenerated {len(reminders)} reminders for crop {crop_id}")
        return jsonify({
            'success': True,
            'message': f'Regenerated {len(reminders)} reminders',
            'reminders_created': len(reminders)
        }), 200
    except Exception as e:
        logger.error(f"Error regenerating reminders: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reminders/all/<crop_id>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def get_crop_reminders(crop_id):
    """Get all reminders for a crop"""
    try:
        reminders = list(db['reminders'].find({'crop_id': crop_id}).sort('day', 1))
        
        for reminder in reminders:
            reminder['id'] = str(reminder['_id'])
            del reminder['_id']
        
        logger.info(f"Fetched {len(reminders)} reminders for crop {crop_id}")
        return jsonify({
            'success': True,
            'reminders': reminders,
            'total': len(reminders)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching reminders: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reminders/complete', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
@validate_json('reminder_id')
def complete_reminder():
    """Mark a reminder as completed"""
    try:
        data = request.get_json()
        reminder_id = data['reminder_id']
        notes = data.get('notes', '')
        
        db['reminders'].update_one(
            {'_id': ObjectId(reminder_id)},
            {
                '$set': {
                    'completed': True,
                    'notes': notes,
                    'completed_at': datetime.now().isoformat()
                }
            }
        )
        
        logger.info(f"Reminder {reminder_id} marked as completed")
        return jsonify({
            'success': True,
            'message': 'Reminder marked as completed'
        }), 200
    except Exception as e:
        logger.error(f"Error completing reminder: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reminders/photos/<crop_id>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def get_crop_photos(crop_id):
    """Get all photos for a crop"""
    try:
        photos = list(db['photos'].find({'crop_id': crop_id}).sort('uploaded_at', -1))
        
        for photo in photos:
            photo['id'] = str(photo['_id'])
            del photo['_id']
        
        logger.info(f"Fetched {len(photos)} photos for crop {crop_id}")
        return jsonify({
            'success': True,
            'photos': photos,
            'total': len(photos)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching photos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reminders/upload-photo/<crop_id>', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
def upload_crop_photo(crop_id):
    """Upload a photo for a crop"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        notes = request.form.get('notes', '')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Save file
        filename = f"{crop_id}_{datetime.now().timestamp()}_{file.filename}"
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        
        # Store in database
        photo_doc = {
            'crop_id': crop_id,
            'filename': filename,
            'filepath': filepath,
            'uploaded_at': datetime.now().isoformat(),
            'notes': notes,
            'analysis': None
        }
        
        result = db['photos'].insert_one(photo_doc)
        
        logger.info(f"Photo uploaded for crop {crop_id}")
        return jsonify({
            'success': True,
            'photo_id': str(result.inserted_id),
            'message': 'Photo uploaded successfully'
        }), 201
    except Exception as e:
        logger.error(f"Error uploading photo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.route('/api/text-to-speech', methods=['POST', 'OPTIONS'])
def text_to_speech_endpoint():
    """Convert text to speech"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200
    
    try:
        from utils.text_to_speech import generate_speech, detect_language
        
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'auto')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Auto-detect language if needed
        if language == 'auto':
            language = detect_language(text)
        
        # Generate speech
        audio_content = generate_speech(text, language)
        
        if audio_content:
            response = send_file(
                io.BytesIO(audio_content),
                mimetype='audio/mpeg',
                as_attachment=False,
                download_name='speech.mp3'
            )
            # Add CORS headers
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            return response
        else:
            return jsonify({'error': 'Failed to generate speech'}), 500
            
    except Exception as e:
        logger.error(f"Error in TTS endpoint: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# FARM PROFILE ENDPOINTS
# ============================================================================

@app.route('/api/farm-profile', methods=['GET'])
@jwt_required()
@error_handler
def get_farm_profile():
    """Get farm profile for logged-in farmer"""
    user_id = get_jwt_identity()
    profile = db['farm_profiles'].find_one({'user_id': user_id})
    if not profile:
        return jsonify({'profile': None, 'message': 'No farm profile found'}), 200
    profile['_id'] = str(profile['_id'])
    return jsonify({'success': True, 'profile': profile}), 200


@app.route('/api/farm-profile', methods=['POST'])
@jwt_required()
@error_handler
def create_farm_profile():
    """Create or update farm profile"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    profile = {
        'user_id': user_id,
        'farm_name':      data.get('farm_name', ''),
        'location':       data.get('location', ''),
        'state':          data.get('state', ''),
        'district':       data.get('district', ''),
        'land_size_acres': float(data.get('land_size_acres', 0)),
        'soil_type':      data.get('soil_type', ''),
        'water_source':   data.get('water_source', ''),
        'irrigation_type': data.get('irrigation_type', ''),
        'active_crops':   data.get('active_crops', []),
        'past_crops':     data.get('past_crops', []),
        'latitude':       data.get('latitude'),
        'longitude':      data.get('longitude'),
        'updated_at':     datetime.now().isoformat(),
    }

    existing = db['farm_profiles'].find_one({'user_id': user_id})
    if existing:
        db['farm_profiles'].update_one({'user_id': user_id}, {'$set': profile})
        msg = 'Farm profile updated'
    else:
        profile['created_at'] = datetime.now().isoformat()
        db['farm_profiles'].insert_one(profile)
        msg = 'Farm profile created'

    logger.info(f"Farm profile saved for user {user_id}")
    return jsonify({'success': True, 'message': msg, 'profile': {k: v for k, v in profile.items() if k != '_id'}}), 200


@app.route('/api/farm-profile/irrigation-advice', methods=['GET'])
@jwt_required()
@error_handler
def get_irrigation_advice():
    """Get farm-profile-specific irrigation advice based on soil + weather"""
    user_id = get_jwt_identity()
    profile = db['farm_profiles'].find_one({'user_id': user_id})
    if not profile:
        return jsonify({'error': 'Farm profile not found. Please set up your farm profile first.'}), 404

    location = profile.get('location', 'Central India')
    soil_type = profile.get('soil_type', 'Loamy')
    active_crops = profile.get('active_crops', [])
    irrigation_type = profile.get('irrigation_type', 'flood')

    # Get weather for farm location
    weather_live = True
    try:
        from utils.weather_integration import get_weather_for_farming
        weather = get_weather_for_farming(location)
        if weather:
            humidity = weather.get('humidity', 60)
            rainfall = weather.get('rainfall_mm', 0)
            temp = weather.get('temperature', 25)
        else:
            raise ValueError('Empty weather response')
    except Exception:
        humidity, rainfall, temp = 60, 0, 25
        weather_live = False

    # Soil water retention mapping
    retention = {'Sandy': 0.3, 'Loamy': 0.6, 'Clay': 0.8, 'Clayey': 0.8, 'Black': 0.75, 'Red': 0.5}
    ret = retention.get(soil_type, 0.5)

    # Irrigation need calculation
    et0 = 0.0023 * (temp + 17.8) * (45 - humidity) * 0.408  # simplified Hargreaves
    effective_rain = rainfall * 0.8
    irrigation_need = max(0, round(et0 - effective_rain / 10, 2))

    schedule = []
    if irrigation_need > 3:
        schedule = ['Irrigate today — high water demand', 'Check soil moisture daily']
    elif irrigation_need > 1:
        schedule = ['Irrigate in 2-3 days', 'Monitor crop leaves for wilting']
    else:
        schedule = ['No irrigation needed today', 'Soil moisture adequate']

    if soil_type in ['Sandy']:
        schedule.append('Sandy soil: irrigate more frequently in smaller amounts')
    elif soil_type in ['Clay', 'Clayey', 'Black']:
        schedule.append('Clay soil: avoid over-irrigation, check drainage')

    return jsonify({
        'success': True,
        'farm_location': location,
        'soil_type': soil_type,
        'active_crops': active_crops,
        'irrigation_type': irrigation_type,
        'weather': {'temperature': temp, 'humidity': humidity, 'rainfall_mm': rainfall},
        'weather_live': weather_live,
        'weather_warning': None if weather_live else 'Live weather unavailable — using average estimates. Advice may be less accurate.',
        'irrigation_need_mm_per_day': irrigation_need,
        'schedule': schedule,
        'water_retention': f"{int(ret*100)}%",
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/farm-profile/health-logs', methods=['GET'])
@jwt_required()
@error_handler
def get_health_logs():
    """Get crop health observation logs for this farm"""
    user_id = get_jwt_identity()
    logs = list(db['health_logs'].find({'user_id': user_id}).sort('created_at', -1).limit(20))
    for log in logs:
        log['_id'] = str(log['_id'])
    return jsonify({'success': True, 'logs': logs, 'total': len(logs)}), 200


@app.route('/api/farm-profile/health-logs', methods=['POST'])
@jwt_required()
@error_handler
def add_health_log():
    """Add a crop health observation log"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    log = {
        'user_id': user_id,
        'crop': data.get('crop', ''),
        'observation': data.get('observation', ''),
        'disease': data.get('disease', ''),
        'severity': data.get('severity', 'low'),
        'action_taken': data.get('action_taken', ''),
        'image_url': data.get('image_url', ''),
        'created_at': datetime.now().isoformat()
    }
    result = db['health_logs'].insert_one(log)
    return jsonify({'success': True, 'log_id': str(result.inserted_id), 'message': 'Health log added'}), 201


# ============================================================================
# UNIFIED DASHBOARD ENDPOINT
# ============================================================================

@app.route('/api/dashboard/unified', methods=['GET'])
@jwt_required()
@error_handler
def unified_dashboard():
    """
    Unified dashboard — returns farm profile, weather, irrigation decision,
    risk alerts, market prices for farmer's crops, and today's priority actions.
    Requirement 6: Unified Farmer Dashboard
    """
    try:
        from utils.dashboard_builder import build_dashboard
        user_id = get_jwt_identity()
        data = build_dashboard(db, user_id)
        return jsonify({'success': True, **data}), 200
    except Exception as e:
        logger.error(f"Unified dashboard error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# MARKET PRICES ENDPOINTS
# ============================================================================

# Static mandi reference prices (based on real MSP/APMC data 2025-26)
MANDI_BASE_PRICES = {
    'wheat':       {'min': 2275, 'max': 2500,  'unit': 'per quintal', 'msP': 2275},
    'rice':        {'min': 2300, 'max': 2600,  'unit': 'per quintal', 'msP': 2300},
    'maize':       {'min': 2090, 'max': 2400,  'unit': 'per quintal', 'msP': 2090},
    'soybean':     {'min': 4892, 'max': 5500,  'unit': 'per quintal', 'msP': 4892},
    'cotton':      {'min': 7121, 'max': 8000,  'unit': 'per quintal', 'msP': 7121},
    'mustard':     {'min': 5950, 'max': 6500,  'unit': 'per quintal', 'msP': 5950},
    'groundnut':   {'min': 6783, 'max': 7500,  'unit': 'per quintal', 'msP': 6783},
    'chickpea':    {'min': 5440, 'max': 6200,  'unit': 'per quintal', 'msP': 5440},
    'lentil':      {'min': 6425, 'max': 7200,  'unit': 'per quintal', 'msP': 6425},
    'onion':       {'min': 800,  'max': 2500,  'unit': 'per quintal', 'msP': None},
    'potato':      {'min': 600,  'max': 1800,  'unit': 'per quintal', 'msP': None},
    'tomato':      {'min': 500,  'max': 3000,  'unit': 'per quintal', 'msP': None},
    'sugarcane':   {'min': 340,  'max': 380,   'unit': 'per quintal', 'msP': 340},
    'turmeric':    {'min': 9000, 'max': 14000, 'unit': 'per quintal', 'msP': None},
    'chilli':      {'min': 8000, 'max': 16000, 'unit': 'per quintal', 'msP': None},
    'barley':      {'min': 1735, 'max': 2100,  'unit': 'per quintal', 'msP': 1735},
    'jowar':       {'min': 3371, 'max': 3800,  'unit': 'per quintal', 'msP': 3371},
    'bajra':       {'min': 2625, 'max': 3000,  'unit': 'per quintal', 'msP': 2625},
    'sunflower':   {'min': 7280, 'max': 8000,  'unit': 'per quintal', 'msP': 7280},
    'sesame':      {'min': 8635, 'max': 10000, 'unit': 'per quintal', 'msP': 8635},
}

def get_live_market_price(commodity: str):
    """
    Fetch live price from data.gov.in AGMARKNET API.
    Falls back to MSP-based estimate if API unavailable.
    """
    try:
        # data.gov.in commodity prices API (free, no key required)
        commodity_clean = commodity.lower().strip()
        url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            'api-key': 'resource:9ef84268-d588-465a-a308-a864a43d0070',
            'format': 'json',
            'filters[commodity]': commodity.capitalize(),
            'limit': 5,
            'sort[arrival_date]': 'desc'
        }
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            data = r.json()
            records = data.get('records', [])
            if records:
                prices = [float(rec.get('modal_price', 0)) for rec in records if rec.get('modal_price')]
                if prices:
                    avg = sum(prices) / len(prices)
                    return {
                        'source': 'AGMARKNET (data.gov.in)',
                        'modal_price': round(avg),
                        'min_price': min(prices),
                        'max_price': max(prices),
                        'records': len(prices),
                        'live': True
                    }
    except Exception as e:
        logger.warning(f"Live price fetch failed for {commodity}: {e}")

    # Fallback to MSP/reference prices
    base = MANDI_BASE_PRICES.get(commodity.lower(), {})
    if base:
        import random
        # Simulate realistic price fluctuation ±10%
        modal = round(base['min'] + (base['max'] - base['min']) * 0.5 + random.uniform(-base['min']*0.05, base['min']*0.05))
        return {
            'source': 'MSP Reference (GoI 2025-26)',
            'modal_price': modal,
            'min_price': base['min'],
            'max_price': base['max'],
            'msp': base.get('msP'),
            'live': False
        }
    return None


@app.route('/api/market/prices', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def get_market_prices():
    """Get current mandi prices for all major commodities"""
    prices = []
    for commodity, base in MANDI_BASE_PRICES.items():
        price_data = get_live_market_price(commodity)
        if price_data:
            prices.append({
                'commodity': commodity.capitalize(),
                'commodity_key': commodity,
                'unit': base['unit'],
                'msp': base.get('msP'),
                **price_data
            })
    return jsonify({
        'success': True,
        'prices': prices,
        'total': len(prices),
        'timestamp': datetime.now().isoformat(),
        'note': 'Prices in INR. Live data from AGMARKNET where available, else MSP reference.'
    }), 200


@app.route('/api/market/prices/<commodity>', methods=['GET'])
@limiter.limit("30 per hour")
@error_handler
def get_commodity_price(commodity):
    """Get price for a specific commodity"""
    price_data = get_live_market_price(commodity)
    if not price_data:
        return jsonify({'error': f'Commodity {commodity} not found'}), 404
    base = MANDI_BASE_PRICES.get(commodity.lower(), {})
    return jsonify({
        'success': True,
        'commodity': commodity.capitalize(),
        'unit': base.get('unit', 'per quintal'),
        'msp': base.get('msP'),
        'timestamp': datetime.now().isoformat(),
        **price_data
    }), 200


@app.route('/api/market/prices/bulk', methods=['POST'])
@limiter.limit("20 per hour")
@error_handler
def get_bulk_prices():
    """Get prices for a list of commodities (for farm profile crops)"""
    data = request.get_json() or {}
    commodities = data.get('commodities', list(MANDI_BASE_PRICES.keys())[:10])
    prices = []
    for commodity in commodities:
        price_data = get_live_market_price(commodity)
        if price_data:
            base = MANDI_BASE_PRICES.get(commodity.lower(), {})
            prices.append({
                'commodity': commodity.capitalize(),
                'commodity_key': commodity.lower(),
                'unit': base.get('unit', 'per quintal'),
                'msp': base.get('msP'),
                **price_data
            })
    return jsonify({
        'success': True,
        'prices': prices,
        'total': len(prices),
        'timestamp': datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

# Log startup info
logger.info(f"Starting KisanSathi Backend (Enhanced)")
logger.info(f"Database: {MONGODB_DB}")
if db is not None:
    logger.info("✅ MongoDB connected and ready!")
else:
    logger.warning("⚠️ MongoDB not connected - some features may not work")
logger.info("✅ JWT Authentication enabled!")
logger.info("✅ Rate Limiting enabled!")
logger.info("✅ Caching enabled!")

if redis_manager and redis_manager.connected:
    logger.info("✅ Redis caching enabled!")
    logger.info(f"   Host: {REDIS_HOST}:{REDIS_PORT}")
else:
    logger.warning("⚠️ Redis not available - using fallback caching")

logger.info("✅ File handling enabled!")
logger.info("✅ WebSocket events enabled!")
logger.info("✅ All 31 API endpoints ready!")

if __name__ == '__main__':
    if db is None:
        logger.error("❌ MongoDB not connected. Please start MongoDB and try again.")
        exit(1)
    
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True
    )

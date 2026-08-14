"""
Farmer groups, messages and group admin.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson.objectid import ObjectId
from extensions import limiter, cache
from database import db
from decorators import error_handler, validate_json

import logging

logger = logging.getLogger(__name__)

community_bp = Blueprint('community', __name__)


@community_bp.route('/api/community/groups', methods=['GET'])
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

@community_bp.route('/api/community/groups', methods=['POST'])
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

@community_bp.route('/api/community/groups/<group_id>/messages', methods=['GET'])
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

@community_bp.route('/api/community/groups/<group_id>/messages', methods=['POST'])
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

@community_bp.route('/api/community/messages/<message_id>', methods=['DELETE'])
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


@community_bp.route('/api/community/groups/<group_id>/add-member', methods=['POST'])
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

@community_bp.route('/api/community/groups/<group_id>/make-admin', methods=['POST'])
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

"""
Crop reminders, photos and regeneration.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

import os

from flask import Blueprint
from flask import request, jsonify
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from extensions import limiter
from database import db
from decorators import error_handler, validate_json

import logging

logger = logging.getLogger(__name__)

reminders_bp = Blueprint('reminders', __name__)


@reminders_bp.route('/api/reminders/available-crops', methods=['GET'])
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

@reminders_bp.route('/api/reminders/crops/<farmer_id>', methods=['GET'])
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

@reminders_bp.route('/api/reminders/add-crop', methods=['POST'])
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

@reminders_bp.route('/api/reminders/regenerate/<crop_id>', methods=['POST'])
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

@reminders_bp.route('/api/reminders/all/<crop_id>', methods=['GET'])
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

@reminders_bp.route('/api/reminders/complete', methods=['POST'])
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

@reminders_bp.route('/api/reminders/photos/<crop_id>', methods=['GET'])
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

@reminders_bp.route('/api/reminders/upload-photo/<crop_id>', methods=['POST'])
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

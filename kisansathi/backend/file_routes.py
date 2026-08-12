"""File Handling Routes with Cloudinary"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils.cloudinary_handler import cloudinary_handler
from datetime import datetime
import os

file_bp = Blueprint('files', __name__, url_prefix='/api/files')

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@file_bp.route('/upload/image', methods=['POST'])
def upload_image():
    """Upload image to Cloudinary"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
        
        if file.content_length > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large. Max 50MB'}), 400
        
        folder = request.form.get('folder', 'kisansathi/images')
        result = cloudinary_handler.upload_image(file, folder=folder)
        
        if result['success']:
            return jsonify({
                'message': 'Image uploaded successfully',
                'data': result
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/upload/video', methods=['POST'])
def upload_video():
    """Upload video to Cloudinary"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            return jsonify({'error': 'Invalid file type. Allowed: mp4, avi, mov, mkv, webm'}), 400
        
        if file.content_length > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large. Max 50MB'}), 400
        
        folder = request.form.get('folder', 'kisansathi/videos')
        result = cloudinary_handler.upload_video(file, folder=folder)
        
        if result['success']:
            return jsonify({
                'message': 'Video uploaded successfully',
                'data': result
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/upload/document', methods=['POST'])
def upload_document():
    """Upload document to Cloudinary"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
            return jsonify({'error': 'Invalid file type. Allowed: pdf, doc, docx, txt, xls, xlsx'}), 400
        
        if file.content_length > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large. Max 50MB'}), 400
        
        folder = request.form.get('folder', 'kisansathi/documents')
        result = cloudinary_handler.upload_document(file, folder=folder)
        
        if result['success']:
            return jsonify({
                'message': 'Document uploaded successfully',
                'data': result
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/delete/<public_id>', methods=['DELETE'])
def delete_file(public_id):
    """Delete file from Cloudinary"""
    try:
        resource_type = request.args.get('type', 'image')
        result = cloudinary_handler.delete_file(public_id, resource_type=resource_type)
        
        if result['success']:
            return jsonify({
                'message': result['message']
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/info/<public_id>', methods=['GET'])
def get_file_info(public_id):
    """Get file information"""
    try:
        result = cloudinary_handler.get_file_info(public_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/list', methods=['GET'])
def list_files():
    """List files in folder"""
    try:
        folder = request.args.get('folder', 'kisansathi')
        max_results = int(request.args.get('max_results', 100))
        
        result = cloudinary_handler.list_files(folder=folder, max_results=max_results)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/upload-url', methods=['GET'])
def get_upload_url():
    """Get unsigned upload URL for direct uploads"""
    try:
        folder = request.args.get('folder', 'kisansathi')
        result = cloudinary_handler.get_upload_url(folder=folder)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/optimize/<public_id>', methods=['GET'])
def optimize_image(public_id):
    """Get optimized image URL"""
    try:
        width = int(request.args.get('width', 800))
        height = int(request.args.get('height', 600))
        
        url = cloudinary_handler.optimize_image_url(public_id, width=width, height=height)
        
        return jsonify({
            'url': url,
            'width': width,
            'height': height
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/thumbnail/<public_id>', methods=['GET'])
def get_thumbnail(public_id):
    """Get thumbnail URL"""
    try:
        size = int(request.args.get('size', 200))
        
        url = cloudinary_handler.get_thumbnail_url(public_id, size=size)
        
        return jsonify({
            'url': url,
            'size': size
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

"""Cloudinary File Handling for KisanSathi"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from typing import Dict, Optional, List

class CloudinaryHandler:
    """Handle file uploads and management with Cloudinary"""
    
    def __init__(self):
        """Initialize Cloudinary configuration"""
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
    
    def upload_image(self, file, folder: str = 'kisansathi', public_id: Optional[str] = None) -> Dict:
        """Upload image to Cloudinary"""
        try:
            options = {
                'folder': folder,
                'resource_type': 'auto',
                'quality': 'auto',
                'fetch_format': 'auto'
            }
            
            if public_id:
                options['public_id'] = public_id
            
            result = cloudinary.uploader.upload(file, **options)
            
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'size': result['bytes'],
                'format': result['format'],
                'width': result.get('width'),
                'height': result.get('height')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_video(self, file, folder: str = 'kisansathi/videos') -> Dict:
        """Upload video to Cloudinary"""
        try:
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                resource_type='video',
                quality='auto'
            )
            
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'size': result['bytes'],
                'duration': result.get('duration'),
                'format': result['format']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_document(self, file, folder: str = 'kisansathi/documents') -> Dict:
        """Upload document (PDF, DOC, etc) to Cloudinary"""
        try:
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                resource_type='raw'
            )
            
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'size': result['bytes'],
                'format': result['format']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, public_id: str, resource_type: str = 'image') -> Dict:
        """Delete file from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            
            return {
                'success': result.get('result') == 'ok',
                'message': f"File {public_id} deleted successfully"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_info(self, public_id: str) -> Dict:
        """Get file information from Cloudinary"""
        try:
            result = cloudinary.api.resource(public_id)
            
            return {
                'success': True,
                'public_id': result['public_id'],
                'url': result['secure_url'],
                'size': result['bytes'],
                'format': result['format'],
                'created_at': result['created_at'],
                'width': result.get('width'),
                'height': result.get('height')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_files(self, folder: str = 'kisansathi', max_results: int = 100) -> Dict:
        """List files in a folder"""
        try:
            result = cloudinary.api.resources(
                type='upload',
                prefix=folder,
                max_results=max_results
            )
            
            files = []
            for resource in result.get('resources', []):
                files.append({
                    'public_id': resource['public_id'],
                    'url': resource['secure_url'],
                    'size': resource['bytes'],
                    'format': resource['format'],
                    'created_at': resource['created_at']
                })
            
            return {
                'success': True,
                'files': files,
                'total': len(files)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_upload_url(self, folder: str = 'kisansathi') -> Dict:
        """Generate unsigned upload URL for direct uploads"""
        try:
            timestamp = int(os.time())
            params = {
                'timestamp': timestamp,
                'folder': folder,
                'unsigned': True,
                'api_key': os.getenv('CLOUDINARY_API_KEY')
            }
            
            return {
                'success': True,
                'upload_url': f"https://api.cloudinary.com/v1_1/{os.getenv('CLOUDINARY_CLOUD_NAME')}/image/upload",
                'params': params
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def optimize_image_url(self, public_id: str, width: int = 800, height: int = 600) -> str:
        """Generate optimized image URL"""
        return cloudinary.CloudinaryResource(public_id).build_url(
            width=width,
            height=height,
            crop='fill',
            quality='auto',
            fetch_format='auto'
        )
    
    def get_thumbnail_url(self, public_id: str, size: int = 200) -> str:
        """Generate thumbnail URL"""
        return cloudinary.CloudinaryResource(public_id).build_url(
            width=size,
            height=size,
            crop='thumb',
            gravity='face',
            quality='auto',
            fetch_format='auto'
        )

# Global instance
cloudinary_handler = CloudinaryHandler()

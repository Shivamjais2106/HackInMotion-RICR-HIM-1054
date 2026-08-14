"""
Crop recommendation (ML, ranked, seasonal) and soil-report extraction.

Routes moved verbatim out of app_enhanced.py; paths, methods, rate limits and
response shapes are unchanged.
"""

from flask import Blueprint
from flask import request, jsonify
from PIL import Image
from io import BytesIO
from extensions import limiter
from decorators import error_handler, validate_json
from gemini_helpers import extract_soil_values_from_image, get_gemini_crop_explanation_hindi
from integrations import get_crop_recommendation_ml, get_seasonal_crop_recommendation

import logging

logger = logging.getLogger(__name__)

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/api/recommendations/advanced-crop', methods=['POST'])
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

@recommendations_bp.route('/api/recommendations/crop', methods=['POST'])
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

@recommendations_bp.route('/api/recommendations/extract-from-image', methods=['POST'])
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

@recommendations_bp.route('/api/recommendations/extract-from-pdf', methods=['POST'])
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

@recommendations_bp.route('/api/recommendations/seasonal-crop', methods=['POST'])
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

@recommendations_bp.route('/api/seasons', methods=['GET'])
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

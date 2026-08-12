"""
Crop Health Analyzer - Analyzes crop images for health status and size
Uses PIL only (no OpenCV dependency)
"""

import numpy as np
from PIL import Image
import io

class CropHealthAnalyzer:
    """Analyzes crop health from images"""
    
    def __init__(self):
        self.health_thresholds = {
            'healthy': {'green_ratio': (0.5, 1.0), 'yellow_ratio': (0.0, 0.2)},
            'stressed': {'green_ratio': (0.3, 0.5), 'yellow_ratio': (0.2, 0.4)},
            'diseased': {'green_ratio': (0.0, 0.3), 'yellow_ratio': (0.4, 1.0)}
        }
    
    def analyze_image(self, image_data):
        """
        Analyze crop image for health status and size
        
        Args:
            image_data: Image file or base64 encoded image
            
        Returns:
            dict with health status, confidence, and recommendations
        """
        try:
            # Convert image data to PIL Image
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Analyze color distribution
            health_status = self._analyze_color_health(img_array)
            
            # Estimate crop size
            size_estimate = self._estimate_crop_size(img_array)
            
            # Get fertilizer recommendations based on health
            recommendations = self._get_health_based_recommendations(health_status, size_estimate)
            
            return {
                'success': True,
                'health_status': health_status['status'],
                'health_confidence': health_status['confidence'],
                'health_details': health_status['details'],
                'size_estimate': size_estimate,
                'recommendations': recommendations,
                'analysis_type': 'Image-based Health Analysis'
            }
        
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return self._get_error_response(str(e))
    
    def _rgb_to_hsv(self, r, g, b):
        """Convert RGB to HSV"""
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2.0
        
        if max_c == min_c:
            h = s = 0.0
        else:
            d = max_c - min_c
            s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            
            if max_c == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_c == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        
        return h * 360, s * 100, l * 100
    
    def _analyze_color_health(self, rgb_image):
        """Analyze color distribution to determine health status"""
        
        # Extract RGB channels
        r = rgb_image[:, :, 0]
        g = rgb_image[:, :, 1]
        b = rgb_image[:, :, 2]
        
        # Calculate green ratio (high G, low R and B)
        # Green pixels: G > R and G > B and G > 100
        green_mask = (g > r) & (g > b) & (g > 100)
        green_pixels = np.count_nonzero(green_mask)
        
        # Calculate yellow ratio (high R and G, low B)
        # Yellow pixels: R > 150 and G > 150 and B < 100
        yellow_mask = (r > 150) & (g > 150) & (b < 100)
        yellow_pixels = np.count_nonzero(yellow_mask)
        
        # Calculate brown/dead ratio (low G, high R)
        # Brown pixels: R > 100 and G < 100 and B < 100
        brown_mask = (r > 100) & (g < 100) & (b < 100)
        brown_pixels = np.count_nonzero(brown_mask)
        
        # Calculate ratios
        total_pixels = rgb_image.shape[0] * rgb_image.shape[1]
        green_ratio = green_pixels / total_pixels if total_pixels > 0 else 0
        yellow_ratio = yellow_pixels / total_pixels if total_pixels > 0 else 0
        brown_ratio = brown_pixels / total_pixels if total_pixels > 0 else 0
        
        # Determine health status
        if green_ratio > 0.5 and yellow_ratio < 0.2:
            status = 'Healthy'
            confidence = min(green_ratio * 100, 95)
            details = {
                'green_coverage': f"{green_ratio*100:.1f}%",
                'yellow_coverage': f"{yellow_ratio*100:.1f}%",
                'assessment': 'Crop shows good green foliage with minimal yellowing'
            }
        elif green_ratio > 0.3 and yellow_ratio < 0.4:
            status = 'Stressed'
            confidence = 70
            details = {
                'green_coverage': f"{green_ratio*100:.1f}%",
                'yellow_coverage': f"{yellow_ratio*100:.1f}%",
                'assessment': 'Crop shows signs of stress - moderate yellowing detected'
            }
        else:
            status = 'Diseased/Unhealthy'
            confidence = 75
            details = {
                'green_coverage': f"{green_ratio*100:.1f}%",
                'yellow_coverage': f"{yellow_ratio*100:.1f}%",
                'assessment': 'Crop shows significant yellowing - possible disease or nutrient deficiency'
            }
        
        return {
            'status': status,
            'confidence': f"{confidence:.1f}%",
            'details': details,
            'green_ratio': green_ratio,
            'yellow_ratio': yellow_ratio
        }
    
    def _estimate_crop_size(self, image_array):
        """Estimate crop size from image"""
        
        height, width = image_array.shape[:2]
        
        # Estimate based on image dimensions and green pixel density
        # This is a simplified estimation
        if height > 500 and width > 500:
            size_category = 'Large'
            size_stage = 'Mature/Flowering'
            estimated_days = '60-90 days'
        elif height > 300 and width > 300:
            size_category = 'Medium'
            size_stage = 'Vegetative/Early Growth'
            estimated_days = '30-60 days'
        else:
            size_category = 'Small'
            size_stage = 'Seedling/Early Stage'
            estimated_days = '0-30 days'
        
        return {
            'category': size_category,
            'growth_stage': size_stage,
            'estimated_age': estimated_days,
            'image_dimensions': f"{width}x{height}px"
        }
    
    def _get_health_based_recommendations(self, health_status, size_estimate):
        """Get fertilizer recommendations based on health and size"""
        
        status = health_status['status']
        size = size_estimate['category']
        
        recommendations = {
            'Healthy': {
                'Small': {
                    'primary': 'NPK 10:10:10 (Balanced)',
                    'quantity': '50-75 kg/hectare',
                    'timing': 'Apply at 2-3 leaf stage',
                    'reason': 'Young healthy crop needs balanced nutrition for strong root development',
                    'nitrogen_focus': 'Moderate',
                    'phosphorus_focus': 'High (for root development)',
                    'potassium_focus': 'Moderate'
                },
                'Medium': {
                    'primary': 'NPK 20:10:10 (Nitrogen-rich)',
                    'quantity': '100-120 kg/hectare',
                    'timing': 'Apply at vegetative stage',
                    'reason': 'Growing healthy crop needs nitrogen for leaf and stem development',
                    'nitrogen_focus': 'High',
                    'phosphorus_focus': 'Moderate',
                    'potassium_focus': 'Moderate'
                },
                'Large': {
                    'primary': 'NPK 10:20:20 (Potassium-rich)',
                    'quantity': '80-100 kg/hectare',
                    'timing': 'Apply at flowering/fruiting stage',
                    'reason': 'Mature healthy crop needs potassium for fruit/grain development and disease resistance',
                    'nitrogen_focus': 'Low',
                    'phosphorus_focus': 'High (for flowering)',
                    'potassium_focus': 'High (for fruit quality)'
                }
            },
            'Stressed': {
                'Small': {
                    'primary': 'Urea + DAP (Nitrogen + Phosphorus)',
                    'quantity': '75-100 kg/hectare',
                    'timing': 'Immediate application + foliar spray',
                    'reason': 'Stressed young crop needs quick nutrient boost for recovery',
                    'nitrogen_focus': 'Very High',
                    'phosphorus_focus': 'High',
                    'potassium_focus': 'Moderate',
                    'additional': 'Apply foliar spray of micronutrients (Zinc, Iron)'
                },
                'Medium': {
                    'primary': 'Urea (Nitrogen) + Foliar Spray',
                    'quantity': '100-150 kg/hectare',
                    'timing': 'Split application - 50% now, 50% after 15 days',
                    'reason': 'Stressed crop needs immediate nitrogen for recovery and growth',
                    'nitrogen_focus': 'Very High',
                    'phosphorus_focus': 'Moderate',
                    'potassium_focus': 'Moderate',
                    'additional': 'Foliar spray with micronutrients every 7-10 days'
                },
                'Large': {
                    'primary': 'Balanced NPK + Micronutrients',
                    'quantity': '80-120 kg/hectare',
                    'timing': 'Immediate + repeat after 10 days',
                    'reason': 'Stressed mature crop needs balanced nutrition and micronutrients for recovery',
                    'nitrogen_focus': 'High',
                    'phosphorus_focus': 'High',
                    'potassium_focus': 'High',
                    'additional': 'Foliar spray with Zinc Sulphate (0.5%) and Iron Sulphate (0.5%)'
                }
            },
            'Diseased/Unhealthy': {
                'Small': {
                    'primary': 'DAP + Micronutrients + Fungicide',
                    'quantity': '100-150 kg/hectare',
                    'timing': 'Immediate application + weekly foliar spray',
                    'reason': 'Diseased young crop needs phosphorus for root strength and micronutrients for disease resistance',
                    'nitrogen_focus': 'Moderate',
                    'phosphorus_focus': 'Very High',
                    'potassium_focus': 'High',
                    'additional': 'Apply fungicide spray immediately. Foliar spray with Zinc (0.5%) and Boron (0.2%)',
                    'warning': 'Consult local agricultural expert for disease identification'
                },
                'Medium': {
                    'primary': 'Balanced NPK + Micronutrients + Disease Management',
                    'quantity': '120-150 kg/hectare',
                    'timing': 'Immediate + repeat after 10 days',
                    'reason': 'Diseased crop needs balanced nutrition and micronutrients for recovery and disease resistance',
                    'nitrogen_focus': 'Moderate',
                    'phosphorus_focus': 'High',
                    'potassium_focus': 'High',
                    'additional': 'Weekly foliar spray with Zinc Sulphate (0.5%), Copper Sulphate (0.3%), and Boron (0.2%)',
                    'warning': 'Identify disease type and apply appropriate fungicide/pesticide'
                },
                'Large': {
                    'primary': 'Potassium-rich NPK + Micronutrients + Disease Control',
                    'quantity': '100-120 kg/hectare',
                    'timing': 'Immediate + repeat after 7-10 days',
                    'reason': 'Diseased mature crop needs potassium for disease resistance and micronutrients for recovery',
                    'nitrogen_focus': 'Low',
                    'phosphorus_focus': 'Moderate',
                    'potassium_focus': 'Very High',
                    'additional': 'Bi-weekly foliar spray with Potassium Nitrate (1%), Zinc (0.5%), and Copper (0.3%)',
                    'warning': 'Urgent: Consult agricultural expert for disease diagnosis and treatment'
                }
            }
        }
        
        # Get recommendation for this combination
        rec = recommendations.get(status, {}).get(size, {})
        
        return {
            'primary_recommendation': rec.get('primary', 'NPK 10:10:10'),
            'quantity': rec.get('quantity', '100 kg/hectare'),
            'timing': rec.get('timing', 'Apply at appropriate growth stage'),
            'reason': rec.get('reason', 'Based on crop health and size'),
            'nutrient_focus': {
                'nitrogen': rec.get('nitrogen_focus', 'Moderate'),
                'phosphorus': rec.get('phosphorus_focus', 'Moderate'),
                'potassium': rec.get('potassium_focus', 'Moderate')
            },
            'additional_measures': rec.get('additional', 'Follow standard agricultural practices'),
            'warning': rec.get('warning', None),
            'health_status': status,
            'crop_size': size
        }
    
    def _get_error_response(self, error_message):
        """Return error response"""
        return {
            'success': False,
            'error': error_message,
            'health_status': 'Unknown',
            'recommendations': {
                'primary_recommendation': 'Unable to analyze - please try with a clearer image',
                'reason': error_message
            }
        }


def analyze_crop_health_from_image(image_data):
    """
    Wrapper function to analyze crop health from image
    
    Args:
        image_data: Image file or bytes
        
    Returns:
        dict with analysis results
    """
    try:
        analyzer = CropHealthAnalyzer()
        result = analyzer.analyze_image(image_data)
        return result
    except Exception as e:
        print(f"Error in crop health analysis: {e}")
        return {
            'success': False,
            'error': str(e),
            'health_status': 'Unknown'
        }

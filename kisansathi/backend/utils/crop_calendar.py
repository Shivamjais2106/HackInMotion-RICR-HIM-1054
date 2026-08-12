"""Crop Calendar for KisanSathi"""

def get_crop_calendar(region="India"):
    """Get seasonal crop calendar for a region"""
    
    calendar = {
        'kharif': {
            'season': 'Monsoon (June-October)',
            'crops': [
                {
                    'name': 'Rice',
                    'sowing': 'June-July',
                    'harvesting': 'October-November',
                    'duration': '120-150 days',
                    'water_requirement': 'High (1000-1500 mm)',
                    'temperature': '20-30°C'
                },
                {
                    'name': 'Maize',
                    'sowing': 'June-July',
                    'harvesting': 'September-October',
                    'duration': '90-120 days',
                    'water_requirement': 'Medium (500-750 mm)',
                    'temperature': '21-27°C'
                },
                {
                    'name': 'Cotton',
                    'sowing': 'May-June',
                    'harvesting': 'December-January',
                    'duration': '180-210 days',
                    'water_requirement': 'High (600-1000 mm)',
                    'temperature': '21-30°C'
                },
                {
                    'name': 'Groundnut',
                    'sowing': 'June-July',
                    'harvesting': 'September-October',
                    'duration': '100-120 days',
                    'water_requirement': 'Medium (500-750 mm)',
                    'temperature': '20-30°C'
                },
                {
                    'name': 'Soybean',
                    'sowing': 'June-July',
                    'harvesting': 'September-October',
                    'duration': '90-110 days',
                    'water_requirement': 'Medium (600-800 mm)',
                    'temperature': '20-30°C'
                }
            ]
        },
        'rabi': {
            'season': 'Winter (October-March)',
            'crops': [
                {
                    'name': 'Wheat',
                    'sowing': 'October-November',
                    'harvesting': 'March-April',
                    'duration': '120-150 days',
                    'water_requirement': 'Low (400-500 mm)',
                    'temperature': '15-25°C'
                },
                {
                    'name': 'Barley',
                    'sowing': 'October-November',
                    'harvesting': 'March-April',
                    'duration': '120-140 days',
                    'water_requirement': 'Low (300-400 mm)',
                    'temperature': '10-20°C'
                },
                {
                    'name': 'Chickpea',
                    'sowing': 'October-November',
                    'harvesting': 'February-March',
                    'duration': '100-120 days',
                    'water_requirement': 'Low (400-500 mm)',
                    'temperature': '15-25°C'
                },
                {
                    'name': 'Mustard',
                    'sowing': 'September-October',
                    'harvesting': 'February-March',
                    'duration': '120-150 days',
                    'water_requirement': 'Low (300-400 mm)',
                    'temperature': '10-25°C'
                },
                {
                    'name': 'Linseed',
                    'sowing': 'October-November',
                    'harvesting': 'March-April',
                    'duration': '120-150 days',
                    'water_requirement': 'Low (400-500 mm)',
                    'temperature': '15-25°C'
                }
            ]
        },
        'summer': {
            'season': 'Summer (March-May)',
            'crops': [
                {
                    'name': 'Sugarcane',
                    'sowing': 'February-March',
                    'harvesting': 'November-December',
                    'duration': '270-300 days',
                    'water_requirement': 'Very High (1500-2250 mm)',
                    'temperature': '20-30°C'
                },
                {
                    'name': 'Watermelon',
                    'sowing': 'February-March',
                    'harvesting': 'May-June',
                    'duration': '70-100 days',
                    'water_requirement': 'High (400-600 mm)',
                    'temperature': '25-35°C'
                },
                {
                    'name': 'Muskmelon',
                    'sowing': 'February-March',
                    'harvesting': 'May-June',
                    'duration': '80-100 days',
                    'water_requirement': 'High (400-600 mm)',
                    'temperature': '25-35°C'
                },
                {
                    'name': 'Okra',
                    'sowing': 'March-April',
                    'harvesting': 'June-August',
                    'duration': '60-90 days',
                    'water_requirement': 'Medium (500-750 mm)',
                    'temperature': '25-35°C'
                }
            ]
        }
    }
    
    return calendar

def get_crops_for_month(month):
    """Get recommended crops for a specific month"""
    
    month_crops = {
        'January': ['Wheat', 'Barley', 'Chickpea', 'Mustard', 'Linseed'],
        'February': ['Wheat', 'Barley', 'Chickpea', 'Sugarcane', 'Watermelon'],
        'March': ['Wheat', 'Chickpea', 'Sugarcane', 'Watermelon', 'Muskmelon'],
        'April': ['Watermelon', 'Muskmelon', 'Okra', 'Sugarcane'],
        'May': ['Watermelon', 'Muskmelon', 'Okra', 'Sugarcane'],
        'June': ['Rice', 'Maize', 'Cotton', 'Groundnut', 'Soybean'],
        'July': ['Rice', 'Maize', 'Cotton', 'Groundnut', 'Soybean'],
        'August': ['Rice', 'Maize', 'Cotton', 'Groundnut', 'Soybean'],
        'September': ['Rice', 'Maize', 'Cotton', 'Groundnut', 'Soybean'],
        'October': ['Rice', 'Wheat', 'Chickpea', 'Mustard', 'Linseed'],
        'November': ['Wheat', 'Barley', 'Chickpea', 'Mustard', 'Linseed'],
        'December': ['Wheat', 'Barley', 'Chickpea', 'Mustard', 'Linseed']
    }
    
    return month_crops.get(month, [])

def get_crop_details(crop_name):
    """Get detailed information about a specific crop"""
    
    crop_details = {
        'Rice': {
            'season': 'Kharif',
            'sowing': 'June-July',
            'harvesting': 'October-November',
            'duration': '120-150 days',
            'water_requirement': '1000-1500 mm',
            'temperature': '20-30°C',
            'soil_type': 'Clay loam to clay',
            'ph_range': '6.0-7.5',
            'nitrogen': 120,
            'phosphorus': 60,
            'potassium': 40,
            'diseases': ['Blast', 'Brown spot', 'Sheath blight'],
            'pests': ['Stem borer', 'Leaf folder', 'Gall midge'],
            'yield': '40-60 quintals/hectare'
        },
        'Wheat': {
            'season': 'Rabi',
            'sowing': 'October-November',
            'harvesting': 'March-April',
            'duration': '120-150 days',
            'water_requirement': '400-500 mm',
            'temperature': '15-25°C',
            'soil_type': 'Well-drained loam',
            'ph_range': '6.0-7.5',
            'nitrogen': 100,
            'phosphorus': 50,
            'potassium': 30,
            'diseases': ['Rust', 'Powdery mildew', 'Septoria'],
            'pests': ['Armyworm', 'Aphid', 'Termite'],
            'yield': '40-50 quintals/hectare'
        },
        'Maize': {
            'season': 'Kharif',
            'sowing': 'June-July',
            'harvesting': 'September-October',
            'duration': '90-120 days',
            'water_requirement': '500-750 mm',
            'temperature': '21-27°C',
            'soil_type': 'Well-drained loam',
            'ph_range': '6.0-7.5',
            'nitrogen': 150,
            'phosphorus': 75,
            'potassium': 50,
            'diseases': ['Leaf blight', 'Rust', 'Stalk rot'],
            'pests': ['Stem borer', 'Armyworm', 'Aphid'],
            'yield': '40-50 quintals/hectare'
        },
        'Cotton': {
            'season': 'Kharif',
            'sowing': 'May-June',
            'harvesting': 'December-January',
            'duration': '180-210 days',
            'water_requirement': '600-1000 mm',
            'temperature': '21-30°C',
            'soil_type': 'Well-drained loam to clay loam',
            'ph_range': '6.0-7.5',
            'nitrogen': 100,
            'phosphorus': 50,
            'potassium': 50,
            'diseases': ['Leaf curl', 'Wilt', 'Boll rot'],
            'pests': ['Bollworm', 'Jassid', 'Whitefly'],
            'yield': '15-20 quintals/hectare'
        },
        'Sugarcane': {
            'season': 'Summer',
            'sowing': 'February-March',
            'harvesting': 'November-December',
            'duration': '270-300 days',
            'water_requirement': '1500-2250 mm',
            'temperature': '20-30°C',
            'soil_type': 'Well-drained loam',
            'ph_range': '6.0-8.0',
            'nitrogen': 150,
            'phosphorus': 75,
            'potassium': 75,
            'diseases': ['Red rot', 'Smut', 'Wilt'],
            'pests': ['Stem borer', 'Scale insect', 'Mealybug'],
            'yield': '60-80 tonnes/hectare'
        }
    }
    
    return crop_details.get(crop_name, {})

def get_seasonal_activities(season):
    """Get recommended farming activities for a season"""
    
    activities = {
        'Kharif': [
            'Prepare field and apply manure',
            'Sow seeds during monsoon',
            'Apply first irrigation if needed',
            'Monitor for pests and diseases',
            'Apply fertilizers as per schedule',
            'Weed control at 30-45 days',
            'Harvest when crop matures'
        ],
        'Rabi': [
            'Prepare field after kharif harvest',
            'Apply basal fertilizers',
            'Sow seeds in October-November',
            'Provide irrigation as needed',
            'Monitor for frost damage',
            'Apply top dressing fertilizers',
            'Harvest in March-April'
        ],
        'Summer': [
            'Prepare field with irrigation',
            'Sow seeds in February-March',
            'Provide frequent irrigation',
            'Apply mulch to conserve moisture',
            'Monitor for heat stress',
            'Control weeds regularly',
            'Harvest in May-June'
        ]
    }
    
    return activities.get(season, [])

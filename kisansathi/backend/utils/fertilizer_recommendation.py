"""Fertilizer Recommendation for KisanSathi"""

import pickle
import os
import pandas as pd
import numpy as np

def get_fertilizer_recommendation(nitrogen, phosphorus, potassium, temperature, humidity, moisture, soil_type, crop_type):
    """Get fertilizer recommendation based on soil and crop parameters using ML model"""
    
    try:
        # Load comprehensive model and encoders
        model_path = os.path.join(os.path.dirname(__file__), '../models/fertilizer_model_xgboost_comprehensive.pkl')
        encoders_path = os.path.join(os.path.dirname(__file__), '../models/fertilizer_encoders_comprehensive.pkl')
        
        if os.path.exists(model_path) and os.path.exists(encoders_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            with open(encoders_path, 'rb') as f:
                encoders_data = pickle.load(f)
            
            label_encoders = encoders_data['label_encoders']
            target_encoder = encoders_data['target_encoder']
            feature_names = encoders_data['feature_names']
            
            # Prepare feature dataframe
            feature_dict = {
                'Nitrogen_Level': nitrogen,
                'Phosphorus_Level': phosphorus,
                'Potassium_Level': potassium,
                'Temperature': temperature,
                'Humidity': humidity,
                'Rainfall': moisture,  # Using moisture as rainfall proxy
                'Soil_Type': soil_type,
                'Soil_pH': 6.5,  # Default value if not provided
                'Soil_Moisture': moisture
            }
            
            # Create dataframe with only required features
            features_df = pd.DataFrame([feature_dict])
            
            # Encode categorical features
            for col in label_encoders.keys():
                if col in features_df.columns:
                    try:
                        features_df[col] = label_encoders[col].transform(features_df[col].astype(str))
                    except:
                        # If encoding fails, use first class as default
                        features_df[col] = 0
            
            # Select only required features in correct order
            X_features = features_df[feature_names]
            
            # Make prediction
            pred_encoded = model.predict(X_features)[0]
            pred_proba = model.predict_proba(X_features)[0]
            pred_fertilizer = target_encoder.inverse_transform([pred_encoded])[0]
            confidence = max(pred_proba) * 100
            
            return {
                'recommended_fertilizer': pred_fertilizer,
                'confidence': f'{confidence:.1f}%',
                'source': 'ML Model (Comprehensive)',
                'details': get_fertilizer_details(pred_fertilizer),
                'application_rate': get_application_rate(crop_type, nitrogen, phosphorus, potassium),
                'timing': get_application_timing(crop_type),
                'precautions': get_fertilizer_precautions(pred_fertilizer)
            }
        else:
            print(f"Model files not found. Using fallback recommendation.")
            return get_default_fertilizer_recommendation(nitrogen, phosphorus, potassium, crop_type)
    
    except Exception as e:
        print(f"Error loading model: {e}")
        return get_default_fertilizer_recommendation(nitrogen, phosphorus, potassium, crop_type)

def get_default_fertilizer_recommendation(n, p, k, crop_type):
    """Get default fertilizer recommendation based on NPK levels"""
    
    recommendation = {
        'recommended_fertilizer': determine_fertilizer_type(n, p, k),
        'confidence': 'Medium',
        'source': 'Rule-based',
        'details': {},
        'application_rate': get_application_rate(crop_type, n, p, k),
        'timing': get_application_timing(crop_type),
        'precautions': []
    }
    
    return recommendation

def determine_fertilizer_type(n, p, k):
    """Determine fertilizer type based on NPK levels"""
    
    if n < 20 and p < 10 and k < 100:
        return "NPK 10:10:10 (Balanced)"
    elif n < 20:
        return "Urea (Nitrogen-rich)"
    elif p < 10:
        return "Superphosphate (Phosphorus-rich)"
    elif k < 100:
        return "Potassium Chloride (Potassium-rich)"
    else:
        return "Organic Fertilizer (Compost/Manure)"

def get_fertilizer_details(fertilizer_type):
    """Get details about specific fertilizer"""
    
    details_map = {
        "Compost": {
            'nitrogen': 2,
            'phosphorus': 1,
            'potassium': 1,
            'description': 'Organic compost for soil enrichment and slow nutrient release',
            'cost': 'Low',
            'benefits': ['Improves soil structure', 'Increases water retention', 'Sustainable']
        },
        "DAP": {
            'nitrogen': 18,
            'phosphorus': 46,
            'potassium': 0,
            'description': 'Di-Ammonium Phosphate - high phosphorus for root development',
            'cost': 'Medium',
            'benefits': ['Promotes root growth', 'Enhances flowering', 'Good for early growth']
        },
        "MOP": {
            'nitrogen': 0,
            'phosphorus': 0,
            'potassium': 60,
            'description': 'Muriate of Potash - high potassium for fruit and disease resistance',
            'cost': 'Medium',
            'benefits': ['Improves fruit quality', 'Increases disease resistance', 'Enhances shelf life']
        },
        "NPK": {
            'nitrogen': 10,
            'phosphorus': 10,
            'potassium': 10,
            'description': 'Balanced NPK fertilizer for general crop growth',
            'cost': 'Low to Medium',
            'benefits': ['Balanced nutrition', 'Suitable for most crops', 'Cost-effective']
        },
        "SSP": {
            'nitrogen': 0,
            'phosphorus': 16,
            'potassium': 0,
            'description': 'Single Super Phosphate - phosphorus-rich for root development',
            'cost': 'Low',
            'benefits': ['Affordable', 'Good phosphorus source', 'Improves root system']
        },
        "Urea": {
            'nitrogen': 46,
            'phosphorus': 0,
            'potassium': 0,
            'description': 'High nitrogen fertilizer for leafy growth and vegetative development',
            'cost': 'Low',
            'benefits': ['High nitrogen content', 'Quick action', 'Affordable']
        },
        "Zinc Sulphate": {
            'nitrogen': 0,
            'phosphorus': 0,
            'potassium': 0,
            'description': 'Micronutrient fertilizer for zinc deficiency correction',
            'cost': 'Medium',
            'benefits': ['Corrects zinc deficiency', 'Improves crop quality', 'Prevents stunted growth']
        }
    }
    
    return details_map.get(fertilizer_type, {
        'nitrogen': 0,
        'phosphorus': 0,
        'potassium': 0,
        'description': f'{fertilizer_type} - ML predicted fertilizer',
        'cost': 'Unknown',
        'benefits': ['ML-based recommendation']
    })

def get_application_rate(crop_type, n, p, k):
    """Get fertilizer application rate based on crop type"""
    
    rates = {
        'rice': {
            'nitrogen': 120,
            'phosphorus': 60,
            'potassium': 40,
            'unit': 'kg/hectare'
        },
        'wheat': {
            'nitrogen': 100,
            'phosphorus': 50,
            'potassium': 30,
            'unit': 'kg/hectare'
        },
        'maize': {
            'nitrogen': 150,
            'phosphorus': 75,
            'potassium': 50,
            'unit': 'kg/hectare'
        },
        'cotton': {
            'nitrogen': 100,
            'phosphorus': 50,
            'potassium': 50,
            'unit': 'kg/hectare'
        },
        'sugarcane': {
            'nitrogen': 150,
            'phosphorus': 75,
            'potassium': 75,
            'unit': 'kg/hectare'
        },
        'vegetables': {
            'nitrogen': 80,
            'phosphorus': 60,
            'potassium': 60,
            'unit': 'kg/hectare'
        }
    }
    
    return rates.get(crop_type.lower(), {
        'nitrogen': 100,
        'phosphorus': 50,
        'potassium': 40,
        'unit': 'kg/hectare'
    })

def get_application_timing(crop_type):
    """Get fertilizer application timing for crop type"""
    
    timing = {
        'rice': [
            'Basal: 50% at planting',
            'Top dressing: 25% at tillering',
            'Top dressing: 25% at panicle initiation'
        ],
        'wheat': [
            'Basal: 50% at sowing',
            'Top dressing: 50% at tillering'
        ],
        'maize': [
            'Basal: 50% at planting',
            'Top dressing: 50% at 6-8 leaf stage'
        ],
        'cotton': [
            'Basal: 50% at planting',
            'Top dressing: 25% at flowering',
            'Top dressing: 25% at boll formation'
        ],
        'sugarcane': [
            'Basal: 100% at planting'
        ],
        'vegetables': [
            'Basal: 50% at planting',
            'Top dressing: 50% at 30-40 days'
        ]
    }
    
    return timing.get(crop_type.lower(), [
        'Basal: 50% at planting',
        'Top dressing: 50% at growth stage'
    ])

def get_fertilizer_precautions(fertilizer_type):
    """Get precautions for specific fertilizer"""
    
    precautions = {
        "Urea": [
            "Apply in split doses to avoid leaching",
            "Water immediately after application",
            "Avoid application during heavy rain",
            "Store in dry place away from moisture"
        ],
        "DAP": [
            "Mix well with soil before application",
            "Apply 2-3 weeks before planting",
            "Avoid contact with skin and eyes",
            "Store in cool, dry place"
        ],
        "MOP": [
            "Apply in split doses",
            "Ensure adequate moisture in soil",
            "Avoid excessive application",
            "Do not mix with acidic fertilizers"
        ],
        "SSP": [
            "Mix well with soil before application",
            "Apply 2-3 weeks before planting",
            "Avoid contact with skin",
            "Store in dry conditions"
        ],
        "NPK": [
            "Follow recommended application rates",
            "Ensure proper soil moisture",
            "Avoid over-application",
            "Apply during appropriate growth stage"
        ],
        "Compost": [
            "Ensure compost is well-decomposed",
            "Apply 2-3 weeks before planting",
            "Mix thoroughly with soil",
            "Use aged compost for best results"
        ],
        "Zinc Sulphate": [
            "Apply as foliar spray or soil application",
            "Use recommended doses only",
            "Avoid contact with eyes",
            "Store away from moisture"
        ]
    }
    
    return precautions.get(fertilizer_type, [
        "Follow recommended application rates",
        "Ensure proper soil moisture",
        "Avoid over-application",
        "Consult local agricultural expert if unsure"
    ])

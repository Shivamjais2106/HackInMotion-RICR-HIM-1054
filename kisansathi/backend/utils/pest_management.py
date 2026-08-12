"""Pest Management for KisanSathi"""

def identify_pest(pest_name):
    """Identify pest and provide management strategies"""
    
    pests = {
        'Stem Borer': {
            'affected_crops': ['Rice', 'Maize', 'Sugarcane'],
            'symptoms': [
                'Holes in stems',
                'Wilting of shoots',
                'Dead hearts in rice',
                'Yellowing of leaves'
            ],
            'damage_level': 'High',
            'management': get_pest_management('Stem Borer')
        },
        'Leaf Folder': {
            'affected_crops': ['Rice'],
            'symptoms': [
                'Folded leaves',
                'Transparent patches',
                'Skeletonized leaves',
                'Reduced photosynthesis'
            ],
            'damage_level': 'Medium',
            'management': get_pest_management('Leaf Folder')
        },
        'Armyworm': {
            'affected_crops': ['Maize', 'Wheat', 'Cotton'],
            'symptoms': [
                'Irregular holes in leaves',
                'Defoliation',
                'Damage to ear/cob',
                'Frass on leaves'
            ],
            'damage_level': 'High',
            'management': get_pest_management('Armyworm')
        },
        'Bollworm': {
            'affected_crops': ['Cotton'],
            'symptoms': [
                'Holes in bolls',
                'Damaged seeds',
                'Rotting bolls',
                'Larva inside bolls'
            ],
            'damage_level': 'Very High',
            'management': get_pest_management('Bollworm')
        },
        'Jassid': {
            'affected_crops': ['Cotton'],
            'symptoms': [
                'Yellowing of leaves',
                'Curling of leaves',
                'Stunted growth',
                'Sticky honeydew'
            ],
            'damage_level': 'High',
            'management': get_pest_management('Jassid')
        },
        'Whitefly': {
            'affected_crops': ['Cotton', 'Vegetables'],
            'symptoms': [
                'Yellowing of leaves',
                'Wilting',
                'Sticky honeydew',
                'Sooty mold'
            ],
            'damage_level': 'High',
            'management': get_pest_management('Whitefly')
        },
        'Aphid': {
            'affected_crops': ['Wheat', 'Maize', 'Vegetables'],
            'symptoms': [
                'Curling of leaves',
                'Yellowing',
                'Stunted growth',
                'Sticky honeydew'
            ],
            'damage_level': 'Medium',
            'management': get_pest_management('Aphid')
        },
        'Termite': {
            'affected_crops': ['Wheat', 'Maize', 'Sugarcane'],
            'symptoms': [
                'Wilting of plants',
                'Tunnels in soil',
                'Damage to roots',
                'Sudden plant death'
            ],
            'damage_level': 'High',
            'management': get_pest_management('Termite')
        },
        'Scale Insect': {
            'affected_crops': ['Sugarcane'],
            'symptoms': [
                'Brown scales on stems',
                'Yellowing of leaves',
                'Reduced growth',
                'Sticky honeydew'
            ],
            'damage_level': 'Medium',
            'management': get_pest_management('Scale Insect')
        },
        'Mealybug': {
            'affected_crops': ['Sugarcane', 'Cotton'],
            'symptoms': [
                'White cottony masses',
                'Yellowing of leaves',
                'Stunted growth',
                'Sticky honeydew'
            ],
            'damage_level': 'Medium',
            'management': get_pest_management('Mealybug')
        }
    }
    
    return pests.get(pest_name, {})

def get_pest_management(pest_name):
    """Get management strategies for a specific pest"""
    
    strategies = {
        'Stem Borer': {
            'cultural': [
                'Destroy crop residues',
                'Deep plowing after harvest',
                'Crop rotation with non-host crops',
                'Avoid late sowing'
            ],
            'biological': [
                'Release Trichogramma parasitoids',
                'Use Bacillus thuringiensis (Bt)',
                'Encourage natural predators'
            ],
            'chemical': [
                'Spray Chlorpyrifos 20 EC (1.5 L/hectare)',
                'Spray Quinalphos 25 EC (1.5 L/hectare)',
                'Apply Carbofuran 3G (25 kg/hectare)'
            ],
            'monitoring': 'Check for dead hearts and holes in stems weekly'
        },
        'Leaf Folder': {
            'cultural': [
                'Remove affected leaves',
                'Maintain field sanitation',
                'Avoid excessive nitrogen'
            ],
            'biological': [
                'Use Bacillus thuringiensis (Bt)',
                'Release parasitoids'
            ],
            'chemical': [
                'Spray Chlorpyrifos 20 EC (1.5 L/hectare)',
                'Spray Monocrotophos 36 SL (1 L/hectare)'
            ],
            'monitoring': 'Check for folded leaves and transparent patches'
        },
        'Armyworm': {
            'cultural': [
                'Plow field after harvest',
                'Remove crop residues',
                'Avoid continuous cropping'
            ],
            'biological': [
                'Use Bacillus thuringiensis (Bt)',
                'Release parasitoids',
                'Encourage natural enemies'
            ],
            'chemical': [
                'Spray Chlorpyrifos 20 EC (1.5 L/hectare)',
                'Spray Spinosad 45 SC (0.5 L/hectare)',
                'Spray Flubendiamide 20 WG (0.5 kg/hectare)'
            ],
            'monitoring': 'Check for irregular holes and defoliation'
        },
        'Bollworm': {
            'cultural': [
                'Destroy crop residues',
                'Remove affected bolls',
                'Crop rotation',
                'Avoid late sowing'
            ],
            'biological': [
                'Release Trichogramma parasitoids',
                'Use Bacillus thuringiensis (Bt)',
                'Encourage natural predators'
            ],
            'chemical': [
                'Spray Chlorpyrifos 20 EC (1.5 L/hectare)',
                'Spray Spinosad 45 SC (0.5 L/hectare)',
                'Spray Flubendiamide 20 WG (0.5 kg/hectare)'
            ],
            'monitoring': 'Check bolls for holes and larvae weekly'
        },
        'Jassid': {
            'cultural': [
                'Remove affected leaves',
                'Maintain field sanitation',
                'Avoid excessive nitrogen'
            ],
            'biological': [
                'Release parasitoids',
                'Encourage natural predators'
            ],
            'chemical': [
                'Spray Dimethoate 30 EC (0.75 L/hectare)',
                'Spray Imidacloprid 17.8 SL (0.5 L/hectare)',
                'Spray Thiamethoxam 25 WG (0.4 kg/hectare)'
            ],
            'monitoring': 'Check for yellowing and curling of leaves'
        },
        'Whitefly': {
            'cultural': [
                'Remove affected leaves',
                'Use yellow sticky traps',
                'Maintain field sanitation'
            ],
            'biological': [
                'Release parasitoids',
                'Use neem oil spray'
            ],
            'chemical': [
                'Spray Imidacloprid 17.8 SL (0.5 L/hectare)',
                'Spray Thiamethoxam 25 WG (0.4 kg/hectare)',
                'Spray Spinosad 45 SC (0.5 L/hectare)'
            ],
            'monitoring': 'Check undersides of leaves for white insects'
        },
        'Aphid': {
            'cultural': [
                'Remove affected leaves',
                'Use reflective mulches',
                'Maintain field sanitation'
            ],
            'biological': [
                'Release ladybugs',
                'Use neem oil spray',
                'Encourage natural predators'
            ],
            'chemical': [
                'Spray Imidacloprid 17.8 SL (0.5 L/hectare)',
                'Spray Dimethoate 30 EC (0.75 L/hectare)',
                'Spray Malathion 50 EC (1 L/hectare)'
            ],
            'monitoring': 'Check for curling and yellowing of leaves'
        },
        'Termite': {
            'cultural': [
                'Deep plowing',
                'Remove crop residues',
                'Avoid waterlogging',
                'Crop rotation'
            ],
            'biological': [
                'Use Beauveria bassiana',
                'Use Metarhizium anisopliae'
            ],
            'chemical': [
                'Apply Chlorpyrifos 20 EC (2 L/hectare)',
                'Apply Carbofuran 3G (25 kg/hectare)',
                'Treat seeds with Imidacloprid'
            ],
            'monitoring': 'Check for wilting and tunnels in soil'
        },
        'Scale Insect': {
            'cultural': [
                'Remove affected stems',
                'Maintain field sanitation',
                'Avoid excessive nitrogen'
            ],
            'biological': [
                'Release parasitoids',
                'Encourage natural predators'
            ],
            'chemical': [
                'Spray Chlorpyrifos 20 EC (1.5 L/hectare)',
                'Spray Malathion 50 EC (1 L/hectare)',
                'Spray Neem oil (5%)'
            ],
            'monitoring': 'Check stems for brown scales'
        },
        'Mealybug': {
            'cultural': [
                'Remove affected parts',
                'Maintain field sanitation',
                'Avoid excessive nitrogen'
            ],
            'biological': [
                'Release parasitoids',
                'Use neem oil spray'
            ],
            'chemical': [
                'Spray Imidacloprid 17.8 SL (0.5 L/hectare)',
                'Spray Spinosad 45 SC (0.5 L/hectare)',
                'Spray Neem oil (5%)'
            ],
            'monitoring': 'Check for white cottony masses'
        }
    }
    
    return strategies.get(pest_name, {
        'cultural': ['Maintain field sanitation', 'Remove affected parts'],
        'biological': ['Use natural predators'],
        'chemical': ['Consult local agricultural expert'],
        'monitoring': 'Monitor regularly for pest presence'
    })

def get_all_pests():
    """Get list of all managed pests"""
    return [
        'Stem Borer',
        'Leaf Folder',
        'Armyworm',
        'Bollworm',
        'Jassid',
        'Whitefly',
        'Aphid',
        'Termite',
        'Scale Insect',
        'Mealybug'
    ]

def get_pests_for_crop(crop_name):
    """Get pests that affect a specific crop"""
    
    crop_pests = {
        'Rice': ['Stem Borer', 'Leaf Folder', 'Gall Midge'],
        'Wheat': ['Armyworm', 'Aphid', 'Termite'],
        'Maize': ['Stem Borer', 'Armyworm', 'Aphid'],
        'Cotton': ['Bollworm', 'Jassid', 'Whitefly', 'Mealybug'],
        'Sugarcane': ['Stem Borer', 'Scale Insect', 'Mealybug'],
        'Vegetables': ['Whitefly', 'Aphid']
    }
    
    return crop_pests.get(crop_name, [])

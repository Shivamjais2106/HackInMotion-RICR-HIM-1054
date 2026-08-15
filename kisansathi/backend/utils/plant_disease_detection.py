"""Plant Disease Detection Utilities

Torch/torchvision have been removed. They were causing Out-Of-Memory
crashes on low-RAM hosts (Render free tier, 512MB) because:
  1. Both detectors were instantiated at *import time*, loading heavy
     ML libraries into memory the moment the Flask app started, before
     any request was even handled.
  2. The general plant-disease detector downloaded a ~98MB pretrained
     ResNet50 (ImageNet) checkpoint on every fresh deploy.
  3. The custom-trained weight files (rice_disease_model.pth,
     plant_disease_model.pth) were not actually present/functional
     anyway (see the "model not found" warning in your deploy logs),
     so the heavy download wasn't even producing usable predictions.

Both functions below now return a clear "not available" response
instead of attempting image classification. Re-enable real detection
later by plugging in a lightweight approach (e.g. a small ONNX/
TFLite model, or an external inference API) once you have a properly
trained + hosted model — that avoids bundling torch/torchvision in
this backend's own memory footprint.
"""

import logging

logger = logging.getLogger(__name__)

# Disease information database (kept — used for reference/lookup elsewhere)
DISEASE_INFO = {
    "Bacterial leaf blight": {
        "description": "Bacterial leaf blight is a serious disease of rice caused by Xanthomonas oryzae pv. oryzae.",
        "symptoms": "Yellow-green lesions on leaves that turn brown and necrotic. Lesions often have a yellow halo.",
        "management": [
            "Use resistant varieties",
            "Practice crop rotation",
            "Remove infected plant debris",
            "Apply copper-based fungicides",
            "Maintain proper water management",
            "Avoid overhead irrigation",
        ],
        "severity": "High",
    },
    "Brown spot": {
        "description": "Brown spot is a fungal disease of rice caused by Bipolaris oryzae.",
        "symptoms": "Small brown spots with a dark border and light center on leaves. Spots may coalesce.",
        "management": [
            "Use disease-free seeds",
            "Apply fungicides like mancozeb",
            "Improve drainage",
            "Avoid excessive nitrogen",
            "Remove infected leaves",
            "Maintain field sanitation",
        ],
        "severity": "Medium",
    },
    "Leaf smut": {
        "description": "Leaf smut is a fungal disease of rice caused by Entyloma oryzae.",
        "symptoms": "Small dark spots on leaves that appear as smudges. Spots may have a yellow halo.",
        "management": [
            "Use resistant varieties",
            "Apply fungicides early",
            "Maintain proper spacing",
            "Improve air circulation",
            "Remove infected leaves",
            "Practice crop rotation",
        ],
        "severity": "Low to Medium",
    },
    "Healthy": {
        "description": "The plant appears to be healthy with no visible signs of disease.",
        "symptoms": "No disease symptoms observed",
        "management": [
            "Continue regular monitoring",
            "Maintain good cultural practices",
            "Ensure proper nutrition",
            "Monitor for early signs of disease",
        ],
        "severity": "None",
    },
}

# General plant disease classes (from PlantVillage dataset) — kept for reference
PLANTVILLAGE_CLASSES = {
    "Apple___Apple_scab": "Apple - Apple Scab",
    "Apple___Black_rot": "Apple - Black Rot",
    "Apple___Cedar_apple_rust": "Apple - Cedar Apple Rust",
    "Apple___healthy": "Apple - Healthy",
    "Blueberry___healthy": "Blueberry - Healthy",
    "Cherry_(including_sour)___Powdery_mildew": "Cherry - Powdery Mildew",
    "Cherry_(including_sour)___healthy": "Cherry - Healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Corn - Cercospora Leaf Spot",
    "Corn_(maize)___Common_rust_": "Corn - Common Rust",
    "Corn_(maize)___Northern_Leaf_Blight": "Corn - Northern Leaf Blight",
    "Corn_(maize)___healthy": "Corn - Healthy",
    "Grape___Black_rot": "Grape - Black Rot",
    "Grape___Esca_(Black_Measles)": "Grape - Esca (Black Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Grape - Leaf Blight",
    "Grape___healthy": "Grape - Healthy",
    "Orange___Haunglongbing_(Citrus_greening)": "Orange - Huanglongbing",
    "Peach___Bacterial_spot": "Peach - Bacterial Spot",
    "Peach___healthy": "Peach - Healthy",
    "Pepper,_bell___Bacterial_spot": "Pepper - Bacterial Spot",
    "Pepper,_bell___healthy": "Pepper - Healthy",
    "Potato___Early_blight": "Potato - Early Blight",
    "Potato___Late_blight": "Potato - Late Blight",
    "Potato___healthy": "Potato - Healthy",
    "Raspberry___healthy": "Raspberry - Healthy",
    "Soybean___healthy": "Soybean - Healthy",
    "Squash___Powdery_mildew": "Squash - Powdery Mildew",
    "Strawberry___Leaf_scorch": "Strawberry - Leaf Scorch",
    "Strawberry___healthy": "Strawberry - Healthy",
    "Tomato___Bacterial_spot": "Tomato - Bacterial Spot",
    "Tomato___Early_blight": "Tomato - Early Blight",
    "Tomato___Late_blight": "Tomato - Late Blight",
    "Tomato___Leaf_Mold": "Tomato - Leaf Mold",
    "Tomato___Septoria_leaf_spot": "Tomato - Septoria Leaf Spot",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Tomato - Spider Mites",
    "Tomato___Target_Spot": "Tomato - Target Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Tomato - Yellow Leaf Curl Virus",
    "Tomato___Tomato_mosaic_virus": "Tomato - Mosaic Virus",
    "Tomato___healthy": "Tomato - Healthy",
}


def detect_rice_disease(image_file):
    """Rice leaf disease detection is currently unavailable (torch-based
    model removed to prevent Out-Of-Memory crashes on deploy)."""
    logger.info("detect_rice_disease called, but ML model is disabled (torch removed)")
    return {
        "success": False,
        "error": "Rice disease image detection is temporarily unavailable on this deployment.",
    }


def detect_plant_disease(image_file):
    """General plant disease detection is currently unavailable (torch-based
    model removed to prevent Out-Of-Memory crashes on deploy)."""
    logger.info("detect_plant_disease called, but ML model is disabled (torch removed)")
    return {
        "success": False,
        "error": "Plant disease image detection is temporarily unavailable on this deployment.",
    }


__all__ = ["detect_rice_disease", "detect_plant_disease", "DISEASE_INFO"]
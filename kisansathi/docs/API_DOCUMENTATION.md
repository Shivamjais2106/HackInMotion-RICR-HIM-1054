# 📘 KisanSathi - Smart Farm Decision Support System
## Enterprise API Specification (`API_DOCUMENTATION.md`)

Welcome to the production-grade API reference for **KisanSathi** (HackInMotion 2026 | Project Code: `RICR-HIM-1054`).  
This specification details all HTTP REST endpoints, WebSocket event handlers, request/response JSON schemas, authentication mechanics, rate limits, and error handling protocols.

---

## 📑 Table of Contents

1. [Architectural Overview & Global Headers](#1-architectural-overview--global-headers)
2. [Authentication & Security Gateway](#2-authentication--security-gateway)
3. [Smart Farm Decision Support System APIs](#3-smart-farm-decision-support-system-apis)
4. [Agronomy & ML Crop Recommender Engine](#4-agronomy--ml-crop-recommender-engine)
5. [Soil Analysis & Vision OCR Extraction](#5-soil-analysis--vision-ocr-extraction)
6. [Plant Pathology & AI Disease Inference](#6-plant-pathology--ai-disease-inference)
7. [Agricultural Weather & Microclimate Radar](#7-agricultural-weather--microclimate-radar)
8. [Real-time Community Chat & WebSocket Protocols](#8-real-time-community-chat--websocket-protocols)
9. [Voice Assistant & Multilingual Speech Pipeline](#9-voice-assistant--multilingual-speech-pipeline)
10. [System Health, Metrics & Rate Limits](#10-system-health-metrics--rate-limits)

---

## 1. Architectural Overview & Global Headers

- **Base URL**: `http://localhost:5000/api`
- **WebSocket Gateway**: `ws://localhost:5000/socket.io`
- **Data Exchange Standard**: `application/json` (UTF-8)
- **Time Format**: ISO 8601 UTC (`YYYY-MM-DDTHH:mm:ss.sssZ`)

### Standard HTTP Headers

| Header Name | Type | Description | Mandatory |
| :--- | :--- | :--- | :---: |
| `Authorization` | String | Bearer JWT Token (`Bearer <access_token>`) | Yes (Protected Endpoints) |
| `Content-Type` | String | Must be `application/json` for POST/PUT requests | Yes |
| `X-Client-Version` | String | Client release identifier (e.g. `5.0.0`) | Optional |
| `X-RateLimit-Limit` | Integer | Returned in response header indicating max requests/min | System |

---

## 2. Authentication & Security Gateway

### 2.1 Register Farmer / User Account
Registers a new user record in MongoDB with encrypted credentials.

- **Endpoint**: `POST /api/auth/register`
- **Auth Required**: No
- **Rate Limit**: 5 requests / hour / IP

#### Request Payload
```json
{
  "name": "Ramesh Kumar",
  "email": "ramesh.kumar@kisansathi.in",
  "mobile": "9876543210",
  "password": "SecurePassword#2026",
  "agriculture_type": "Organic Farming & Horticulture",
  "location": "Karnal, Haryana"
}
```

#### Response `201 Created`
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "64f1a2b3c4d5e6f7a8b9c0d1",
  "timestamp": "2026-08-14T00:45:00.000Z"
}
```

---

### 2.2 User Authentication & JWT Generation
Authenticates credentials and returns a signed 30-day JWT Access Token.

- **Endpoint**: `POST /api/auth/login`
- **Auth Required**: No
- **Rate Limit**: 10 requests / hour / IP

#### Request Payload
```json
{
  "mobile": "9876543210",
  "password": "SecurePassword#2026"
}
```

#### Response `200 OK`
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMzYwNTkwMCwianRpIjoi...",
  "token_type": "Bearer",
  "user_id": "64f1a2b3c4d5e6f7a8b9c0d1",
  "name": "Ramesh Kumar",
  "mobile": "9876543210"
}
```

---

## 3. Smart Farm Decision Support System APIs

### 3.1 Fetch Farm Profile Specifications
Returns persistent land dimensions, soil texture, pH, crop rotations, and pump capacity.

- **Endpoint**: `GET /api/farm/profile`
- **Auth Required**: Optional
- **Query Parameters**: `user_id` (string, default: `demo_farmer`)

#### Response `200 OK`
```json
{
  "success": true,
  "farm_profile": {
    "user_id": "demo_farmer",
    "farmer_name": "Ramesh Kumar",
    "farm_name": "Green Meadows Farm",
    "location": {
      "district": "Karnal",
      "state": "Haryana",
      "lat": 29.6857,
      "lon": 76.9907
    },
    "land_size_acres": 5.0,
    "soil_type": "Loam",
    "soil_ph": 6.8,
    "primary_crops": ["Wheat", "Mustard", "Tomato"],
    "irrigation_type": "Drip",
    "pump_flow_rate_lph": 5000.0,
    "updated_at": "2026-08-14T00:15:00.000Z"
  }
}
```

---

### 3.2 Persist / Update Farm Profile
Saves new land specifications driving irrigation and climate algorithms.

- **Endpoint**: `POST /api/farm/profile`
- **Auth Required**: Optional

#### Request Payload
```json
{
  "user_id": "demo_farmer",
  "farmer_name": "Ramesh Kumar",
  "farm_name": "Green Meadows Farm",
  "location": {
    "district": "Karnal",
    "state": "Haryana"
  },
  "land_size_acres": 7.5,
  "soil_type": "Loam",
  "soil_ph": 6.8,
  "primary_crops": ["Wheat", "Mustard", "Tomato"],
  "irrigation_type": "Drip",
  "pump_flow_rate_lph": 6000.0
}
```

---

### 3.3 Unified Farmer Decision Dashboard Payload
Single-call aggregated payload bringing together Evapotranspiration calculations, Microclimate Hazard Matrix, Mandi APMC Prices, and Farm Observation Logs.

- **Endpoint**: `GET /api/farm/decision/dashboard`
- **Query Parameters**:
  - `user_id` (string, default: `demo_farmer`)
  - `city` (string, default: `Karnal`)

#### Response `200 OK`
```json
{
  "system": "KisanSathi Smart Farm Decision Support System",
  "version": "5.0.0-HIM-1054",
  "farm_profile": { ... },
  "smart_irrigation": {
    "status": "IRRIGATE 2.5 HOURS TODAY",
    "irrigation_needed": true,
    "target_crop": "Wheat",
    "et0_mm_per_day": 4.2,
    "crop_coefficient_kc": 1.15,
    "etc_mm_per_day": 4.83,
    "water_required_liters_per_acre": 19520,
    "total_water_required_liters": 97600,
    "recommended_pump_hours": 2.5,
    "soil_type": "Loam",
    "land_acres": 5.0,
    "action_reason": "Evapotranspiration rate is 4.2 mm/day under clear sunny weather conditions."
  },
  "climate_risk": {
    "overall_risk_level": "MEDIUM",
    "active_threat_count": 2,
    "threats": [
      {
        "title": "High Fungal & Late Blight Threat",
        "level": "HIGH",
        "category": "Pest & Disease",
        "description": "High atmospheric humidity (74%) creates optimal microclimate for spore germination.",
        "action": "Apply preventive Copper Oxychloride spray."
      }
    ]
  },
  "market_intelligence": {
    "mandi_location": "Karnal, Haryana",
    "commodities": [
      {
        "crop_name": "Wheat",
        "apmc": "Karnal Mandi",
        "min_price": 2275,
        "max_price": 2450,
        "modal_price": 2380,
        "trend": "Bullish",
        "change_pct": 2.4,
        "advisory": "High demand from grain millers. Optimal selling window.",
        "history_7d": [
          {"day": "Mon", "price": 2320},
          {"day": "Tue", "price": 2335},
          {"day": "Wed", "price": 2350},
          {"day": "Thu", "price": 2340},
          {"day": "Fri", "price": 2365},
          {"day": "Sat", "price": 2375},
          {"day": "Sun", "price": 2380}
        ]
      }
    ]
  }
}
```

---

## 4. Agronomy & ML Crop Recommender Engine

### 4.1 Advanced Seasonal Crop Recommendation
- **Endpoint**: `POST /api/recommendations/advanced-crop`
- **Request Payload**:
```json
{
  "month": "October",
  "location": "North India",
  "N": 60,
  "P": 40,
  "K": 40,
  "ph": 6.8
}
```
- **Response `200 OK`**:
```json
{
  "recommended_crops": ["Wheat", "Mustard", "Gram"],
  "primary_recommendation": "Wheat",
  "suitability_score": 94.5,
  "explanation": "Optimal temperature and high nitrogen favor Wheat germination during October."
}
```

---

## 5. Soil Analysis & Vision OCR Extraction

### 5.1 Gemini 2.5 Vision Soil Report OCR
- **Endpoint**: `POST /api/soil/extract-from-image`
- **Request Payload**:
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
}
```
- **Response `200 OK`**:
```json
{
  "success": true,
  "values": {
    "nitrogen": 65,
    "phosphorus": 35,
    "potassium": 45,
    "ph": 6.8
  }
}
```

---

## 6. System Health & Rate Limits

### 6.1 Health Check
- **Endpoint**: `GET /api/health`
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "timestamp": "2026-08-14T00:45:00.000Z",
  "database": "MongoDB",
  "version": "5.0.0"
}
```

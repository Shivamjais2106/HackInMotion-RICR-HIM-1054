# 🗄️ KisanSathi - Complete Database Schema (`DATABASE_SCHEMA.md`)

This document defines the **MongoDB Database Architecture**, entity relationships, collection schemas, and indexing strategies powering **KisanSathi**.

---

## 📌 Database Topology & Storage Layer
- **Primary Database**: MongoDB v6.0+
- **Database Name**: `kisansathi`
- **In-Memory Cache & Session Store**: Redis v7.0 (ET0 calculation cache & SocketIO session state)

---

## 📂 Entity Collections & Schemas

### 1. `users` Collection
Stores farmer user accounts, authentication hashes, and profile settings.

```json
{
  "_id": { "$oid": "64f1a2b3c4d5e6f7a8b9c0d1" },
  "name": "Ramesh Kumar",
  "email": "ramesh.kumar@kisansathi.in",
  "mobile": "9876543210",
  "password": "$2b$12$eImiTXuWVxfM37uY4JANjO5E...",
  "agriculture_type": "Organic Farming & Horticulture",
  "location": "Karnal, Haryana",
  "created_at": "2026-08-12T10:00:00.000Z",
  "updated_at": "2026-08-14T00:45:00.000Z"
}
```

#### Collection Indexes
- Unique Index: `{ "email": 1 }`
- Unique Index: `{ "mobile": 1 }`

---

### 2. `farm_profiles` Collection
Stores persistent farm dimensions, soil texture, pH, crop rotation cycles, and irrigation system parameters.

```json
{
  "_id": { "$oid": "64f2b3c4d5e6f7a8b9c0d1e2" },
  "user_id": "64f1a2b3c4d5e6f7a8b9c0d1",
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
```

#### Collection Indexes
- Unique Index: `{ "user_id": 1 }`
- Compound Index: `{ "location.state": 1, "location.district": 1 }`

---

### 3. `observation_logs` Collection
Stores crop health photo scans, AI diagnosis results, and soil OCR records linked to the farm.

```json
{
  "_id": { "$oid": "64f3c4d5e6f7a8b9c0d1e2f3" },
  "user_id": "64f1a2b3c4d5e6f7a8b9c0d1",
  "crop_name": "Tomato",
  "scan_type": "Disease Scan",
  "diagnosis": "Tomato Early Blight",
  "confidence": 0.958,
  "recommendation": "Apply Mancozeb 75% WP @ 2g/L water every 10 days.",
  "image_url": "data:image/jpeg;base64,...",
  "timestamp": "2026-08-14T00:30:00.000Z"
}
```

#### Collection Indexes
- Index: `{ "user_id": 1, "timestamp": -1 }`

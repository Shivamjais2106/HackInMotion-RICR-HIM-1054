# KisanSathi — Smart Farm Decision Support System
### HackInMotion 2026 | Theme: Agriculture & Farming | Project Code: RICR-HIM-1054

![Tech Stack](https://img.shields.io/badge/Stack-React_18_%7C_Vite_%7C_Flask_%7C_MongoDB-blue.svg)
![Theme](https://img.shields.io/badge/Theme-Agriculture_%26_Farming-emerald.svg)

**KisanSathi** is an end-to-end Smart Farm Decision Support System built to give farmers real-time, personalized agricultural guidance. Instead of generic advice, it combines a persistent **Farm Profile** (location, land size, soil type, active crops) with ML-based crop and fertilizer recommendations, real weather-driven irrigation guidance, image-based disease detection, and live mandi market prices — all in one unified dashboard.

---

## Problem Statement

Indian farmers lack real-time, personalized decision support. KisanSathi addresses this by combining ML-based crop recommendations, live weather data, disease detection, and market price insights into a single dashboard tailored to each farmer's soil, location, and crop history.

---

## Features

| Feature | Status | Description |
|---|:---:|---|
| Farm Profile | ✅ | Location, land size, soil type, active crops |
| ML Crop Recommendation | ✅ | XGBoost model — manual, by location, by month |
| Weather + Irrigation | ✅ | Real WeatherAPI data, farm-profile-specific irrigation advice |
| Disease Detection | ✅ | Image-based plant disease detection (ResNet50 + XGBoost) |
| Fertilizer Recommendation | ✅ | ML-based NPK analysis |
| Soil Analysis | ✅ | Dual-model crop + fertilizer prediction |
| Market Prices | ✅ | Real-time mandi prices via commodity API |
| Unified Dashboard | ✅ | Weather + crop health + market trends in one view |
| Community | ✅ | Farmer groups + messaging |
| Smart Reminders | ✅ | Crop lifecycle reminders |
| Voice Assistant | ✅ | Hindi + English TTS/voice input |
| Livestock Health | ✅ | Disease detection for cattle |

---

## Tech Stack

**Frontend**
- React 18 + TypeScript + Vite
- TailwindCSS + shadcn/ui
- JWT authentication

**Backend**
- Python 3.10+ / Flask 3.1
- Flask-JWT-Extended, Flask-SocketIO, Flask-Limiter
- ML: XGBoost, scikit-learn, PyTorch (ResNet50, MobileNetV2)

**Data & AI**
- MongoDB Atlas (primary database)
- Google Gemini 2.5 Flash (AI explanations)
- WeatherAPI (real-time weather)
- Cloudinary (image storage)
- gTTS (text-to-speech)

---

## Project Structure

```
HackInMotion-RICR-HIM-1054/
├── kisansathi/
│   ├── backend/                  # Flask API server
│   │   ├── app.py                # Main application entrypoint
│   │   ├── utils/                # ML models + utilities
│   │   ├── models/                # Trained .pkl / .pth model files
│   │   └── .env.example          # Environment variable template
│   ├── frontend/
│   │   └── pixel-perfect-copy/   # React + TypeScript frontend
│   │       └── src/
│   │           ├── pages/         # Page components
│   │           ├── components/    # Reusable UI components
│   │           └── utils/         # API utilities
│   ├── pet-health-advisor/       # Pet health sub-module
│   └── docs/                     # Architecture, API docs, requirements
└── README.md
```

---

## Getting Started

### Prerequisites
- Node.js v18+ and npm
- Python 3.10+
- MongoDB (local or Atlas URI)

### Backend Setup
```bash
cd kisansathi/backend
cp .env.example .env      # fill in your own API keys — never commit this file
pip install -r requirements.txt
python app.py             # runs on http://localhost:5000
```

### Frontend Setup
```bash
cd kisansathi/frontend/pixel-perfect-copy
cp .env.example .env      # set VITE_API_URL=http://localhost:5000
npm install --legacy-peer-deps
npm run dev                # runs on http://localhost:5173 (or 8080)
```

### Verify Build
```bash
cd kisansathi/frontend/pixel-perfect-copy
npm run build
```

---

## API Reference

Full endpoint reference: `kisansathi/docs/API_DOCUMENTATION.md`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register farmer |
| POST | `/api/auth/login` | Login |
| GET/POST | `/api/farm-profile` | Farm profile CRUD |
| POST | `/api/recommendations/crop` | ML crop recommendation |
| POST | `/api/recommendations/advanced-crop` | Location + season based |
| POST | `/api/soil/analyze` | Soil analysis |
| POST | `/api/fertilizer/recommend` | Fertilizer recommendation |
| POST | `/api/disease-predict` | Plant disease detection from image |
| GET | `/api/weather/{location}` | Real-time weather |
| GET | `/api/market/prices` | Live mandi prices |
| GET | `/api/dashboard/unified` | Unified dashboard data |

---

## ML Models

| Model | Algorithm | Use Case |
|---|---|---|
| Crop Recommendation | XGBoost | NPK + weather → crop suggestion |
| Fertilizer Recommendation | XGBoost | Soil params → fertilizer |
| Soil Analysis | Random Forest | Soil type → crop + fertilizer |
| Disease Detection | ResNet50 + XGBoost | Image → disease diagnosis |
| Seasonal Crop | Random Forest | Season + month → recommended crops |

---

## System Architecture

See `kisansathi/docs/SYSTEM_ARCHITECTURE.md` for the full architecture diagram and data flow.

---

## Team — RICR-HIM-1054

| Member | Role |
|---|---|
| Shivam Jaiswal | Team Lead — Backend + ML Models |
| Bhoomi Kesharwani | Backend + Weather Integration |
| Sumit Dangi | Frontend + Integration |
| Rustam Ali | Security + Auth + DevOps |

---

## License

This project was built for HackInMotion 2026 (Theme: Agriculture & Farming).
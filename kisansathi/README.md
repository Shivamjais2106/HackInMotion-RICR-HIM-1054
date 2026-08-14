# KisanSathi — Smart Farm Decision Support System

> **HackInMotion 2026** | Theme: Agriculture & Farming | Team Code: **RICR-HIM-1054**

[![Theme](https://img.shields.io/badge/Theme-Agriculture_%26_Farming-green)](https://hackinmotion.in)
[![Stack](https://img.shields.io/badge/Stack-React_18_%7C_Flask_%7C_MongoDB_%7C_XGBoost-blue)](#tech-stack)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Problem Statement

> *"A farmer's biggest risk isn't hard work — it's making the wrong decision at the wrong time."*

Indian farmers — especially small and mid-sized landholders — make critical decisions (which crop to plant, when to irrigate, whether a plant disease is spreading, when to sell) based on experience and guesswork. The data that could help exists, but it is scattered, inaccessible, or not actionable in the moment a decision must be made.

**KisanSathi** is a unified, full-stack Smart Farm Decision Support System that combines real weather data, ML-based crop and disease intelligence, live market prices, and a persistent farm profile into a single dashboard — giving every farmer a knowledgeable advisor available 24/7.

---

## Deliverables

| # | Deliverable | Link |
|---|---|---|
| 1 | Architecture Diagram | [docs/architecture-diagram.png](docs/architecture-diagram.png) |
| 2 | API Documentation | [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) |
| 3 | System Architecture | [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) |
| 4 | Database Schema | [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) |
| 5 | Product Requirements | [docs/PRODUCT_REQUIREMENTS.md](docs/PRODUCT_REQUIREMENTS.md) |
| 6 | README (this file) | [README.md](README.md) |

---

## Key Features (All 9 Must-Haves Implemented)

### 1. User Accounts & Authentication ✅
- Secure sign-up and login via **JWT** (Flask-JWT-Extended)
- Passwords hashed with **bcrypt** — never stored in plaintext
- Per-farmer private data — all profile and log endpoints require a valid JWT
- Token expiry + 401 auto-redirect on the frontend

### 2. Farm Profile Setup ✅
- Farmer configures: location, state, district, land size (acres), soil type, water source, irrigation type, active crops, and past crops
- Profile is stored in MongoDB and drives **all** personalized recommendations — weather, irrigation, crop advice, and market suggestions are all farm-specific, not generic
- Frontend: `/farm-profile` page with bilingual (Hindi/English) UI

### 3. Weather-Based Irrigation & Risk Engine ✅
**API Used: [WeatherAPI.com](https://www.weatherapi.com/)**

**Why WeatherAPI.com?**
- Free tier covers current conditions + 3-day forecast with a single endpoint
- Returns `precip_mm`, `humidity`, `temp_c`, `feelslike_c` — all fields needed for the Hargreaves ET₀ formula
- Low latency, high uptime, well-documented JSON response
- Alternatives evaluated: OpenWeatherMap (no forecast on free tier), Open-Meteo (no Indian city coverage for many rural locations), AgroMonitoring (paid)

**How it's integrated:**
- `backend/utils/weather_integration.py` calls `/v1/current.json` and `/v1/forecast.json`
- Live data feeds the **Hargreaves ET₀ irrigation engine** in `app_enhanced.py → /api/farm-profile/irrigation-advice`:
  ```
  ET₀ = 0.0023 × (T + 17.8) × (Tmax − Tmin) × Ra^0.5   [simplified]
  irrigation_need_mm = max(0, ET₀ − effective_rainfall)
  ```
- Output: daily irrigation need in mm, farm-specific schedule ("irrigate today", "can wait 2 days"), soil-type-adjusted retention advice
- Risk alerts: frost (<0°C), heat stress (>40°C), high humidity fungal risk (>90%)
- Endpoint: `GET /api/weather/{location}`, `GET /api/farm-profile/irrigation-advice`

### 4. Crop Health Monitoring ✅
**Approach: ML model (ResNet50 feature extractor + XGBoost classifier) + Google Gemini 2.5 Vision**

- Farmer uploads 1–5 leaf/crop photos via the Disease page
- `backend/utils/disease_detection_ml.py` runs the XGBoost model trained on PlantVillage dataset (38 disease classes, 85%+ accuracy)
- `backend/utils/plant_disease_detection.py` runs a rice-specific ResNet50 model for paddy diseases
- Google Gemini 2.5 Flash Vision used for soil report OCR (extract NPK/pH values from photo)
- Crop health logs stored in MongoDB `health_logs` collection, linked to the farm profile
- Frontend: `/disease` page (multi-file upload, per-image predictions, confidence scores, management advice)
- Endpoint: `POST /api/disease-predict`, `POST /api/rice-disease-predict`

### 5. Market Price Insights ✅
**Data Source: [AGMARKNET via data.gov.in](https://data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070) + GoI MSP Reference (2025-26)**

**Why this source?**
- AGMARKNET is the official Government of India agricultural market price database — trusted, free, no API key required
- Covers 20+ major commodities across regional Mandis with modal/min/max prices
- Alternatives evaluated: Quandl (discontinued India commodity data), Bloomberg (paid), scraping state portals (fragile)

**How it's integrated:**
- `backend/utils/market_prices.py` — standalone module with `get_live_price()` (AGMARKNET), `get_reference_price()` (MSP fallback ±5% realistic fluctuation), and `get_trade_advice()` (sell/hold advisory)
- 20 commodities tracked: Wheat, Rice, Maize, Soybean, Cotton, Mustard, Groundnut, Chickpea, Lentil, Onion, Potato, Tomato, Sugarcane, Turmeric, Chilli, Barley, Jowar, Bajra, Sunflower, Sesame
- Trade advisory logic: compares modal price vs MSP and seasonal max to generate "Optimal selling window" / "Hold" / "Below MSP — use procurement channel" guidance
- Endpoints: `GET /api/market/prices`, `GET /api/market/prices/{commodity}`, `POST /api/market/prices/bulk`
- Frontend: Market prices section on Dashboard and Shop page with Recharts trend visualization

### 6. Unified Farmer Dashboard ✅
`/dashboard` — Single page showing everything a farmer needs to act on today:
- **Farm profile status** (crops, location, soil type)
- **Live weather card** (temperature, humidity, rainfall — from WeatherAPI.com)
- **Irrigation advice card** (mm/day need, schedule, soil-adjusted guidance)
- **Crop health flag** (latest disease detection result or health log)
- **Market prices table** (top 10 commodities with trade advisory badges)
- **Smart crop recommendation** (ML-based, auto-triggered by farm profile month + location)

### 7. Database Integration ✅
MongoDB Atlas — persistent storage for:
- `users` — farmer accounts (bcrypt-hashed passwords)
- `farm_profiles` — per-user farm setup
- `health_logs` — crop observation history with disease flags
- `groups` + `messages` — community chat
- `crops` + `reminders` — smart reminder system
- `photos` — crop photo upload records
- `history` — AI chatbot conversation history

### 8. Responsive, Clean UI ✅
- React 18 + TypeScript + TailwindCSS + shadcn/ui component library
- Mobile-first layout — tested at 375px (iPhone SE) and 768px (tablet)
- Color-coded alerts: 🔴 High risk, 🟡 Warning, 🟢 Safe
- Hindi/English bilingual toggle on all key pages (Farm Profile, Dashboard, Voice Assistant)
- TTS (gTTS) — reads out recommendations for low-literacy users

### 9. Error Handling ✅
- All API endpoints wrapped in `@error_handler` decorator — never returns a blank 500
- Weather service failure → `503` with clear message, dashboard shows cached/fallback data
- Failed image upload → user-facing error with retry prompt
- JWT expiry → automatic redirect to `/auth` login page
- Missing farm profile → friendly prompt to set up profile before using advanced features
- API rate limits → `429` with "try again later" message

---

## Bonus Challenges Implemented

| Challenge | Status | Notes |
|---|---|---|
| Crop Recommendation Engine | ✅ | XGBoost model — by soil NPK/pH, by month, by location + season |
| Voice-Based Interface | ✅ | Hindi + English TTS via gTTS; speech recognition via Web Speech API |
| Pest / Disease Alerts | ✅ | Community groups — farmers report issues; Pest Management module |
| Fertilizer & Resource Planning | ✅ | ML-based NPK → fertilizer recommendation (`/api/fertilizer/recommend`) |
| Yield Prediction | ⚠️ | Partial — crop calendar + growth stage tracking, no yield number yet |
| Offline-First Support | ⚠️ | Partial — UI degrades gracefully; no service worker yet |

---

## System Architecture

![Architecture Diagram](docs/architecture-diagram.png)

```
┌─────────────────────────────────────────────────────────────┐
│                    React 18 + Vite Frontend                 │
│  Dashboard │ Farm Profile │ Disease │ Weather │ Market      │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS / JWT
┌───────────────────────▼─────────────────────────────────────┐
│              Flask REST API  (app_enhanced.py)              │
│  Auth │ Farm Profile │ Recommendations │ Weather │ Market   │
│  Disease Detection │ Chatbot │ Community │ Reminders        │
└──────┬──────────────┬───────────────┬───────────────────────┘
       │              │               │
  MongoDB Atlas   WeatherAPI.com   AGMARKNET
  (persistent     (live weather    (commodity
   storage)        + forecast)      prices)
       │
  ML Models (.pkl / .pth)
  XGBoost │ Random Forest │ ResNet50
  Crop Rec │ Fertilizer │ Disease Detection
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React 18 + TypeScript + Vite | Fast HMR, type safety, component reuse |
| Styling | TailwindCSS + shadcn/ui | Rapid mobile-first UI, accessible components |
| State / Data | TanStack Query v5 | Server-state caching, auto-refetch |
| Backend | Python 3.10+ + Flask 2.3 | Mature ML ecosystem, Flask-JWT, rate limiting |
| Auth | Flask-JWT-Extended + bcrypt | Stateless JWT, secure password hashing |
| Database | MongoDB Atlas | Flexible schema for farm profiles + logs |
| ML | XGBoost 2.0 + scikit-learn 1.3 + PyTorch 2.2 | State-of-art tabular ML + image classification |
| Weather API | WeatherAPI.com | Free tier, forecast + current, Indian city coverage |
| Market Data | AGMARKNET (data.gov.in) | Official GoI source, free, modal/min/max prices |
| AI / Vision | Google Gemini 2.5 Flash | Soil OCR, Hindi crop explanations |
| Image Storage | Cloudinary | CDN-backed uploads, transformation API |
| TTS | gTTS | Hindi + English voice output |
| Real-time | Flask-SocketIO + Socket.IO | Community chat, live notifications |
| Caching | Flask-Caching + Redis | Reduce weather/market API calls |
| Linting | Ruff + Flake8 (Python), ESLint 9 (TS) | Code quality enforcement |
| Deployment | Render (backend) + Vercel (frontend) | Free tier, auto-deploy from GitHub |

---

## Project Structure

```
HackInMotion-RICR-HIM-1054/
├── README.md
├── CONTRIBUTING.md
├── .gitignore
└── kisansathi/
    ├── README.md                         ← This file
    ├── backend/
    │   ├── app_enhanced.py               ← Main Flask app (57 API endpoints)
    │   ├── config.py                     ← Config loaded from .env (no secrets)
    │   ├── requirements.txt              ← All Python dependencies
    │   ├── ruff.toml                     ← Python linter config
    │   ├── setup.cfg                     ← Flake8 config
    │   ├── utils/
    │   │   ├── weather_integration.py    ← WeatherAPI.com integration
    │   │   ├── market_prices.py          ← AGMARKNET + MSP market prices
    │   │   ├── crop_recommendation_ml.py ← XGBoost crop model
    │   │   ├── disease_detection_ml.py   ← XGBoost disease model
    │   │   ├── fertilizer_recommendation.py
    │   │   ├── soil_analysis.py
    │   │   ├── input_validator.py        ← Centralised input validation
    │   │   └── ...
    │   ├── models/                       ← Trained .pkl / .pth model files
    │   └── .env.example                  ← Template — copy to .env, fill keys
    ├── frontend/
    │   └── pixel-perfect-copy/
    │       ├── eslint.config.js          ← ESLint 9 flat config
    │       ├── src/
    │       │   ├── pages/
    │       │   │   ├── DashboardEnhanced.tsx  ← Unified dashboard
    │       │   │   ├── FarmProfilePage.tsx    ← Farm setup + irrigation advice
    │       │   │   ├── DiseasePage.tsx        ← Crop health monitoring
    │       │   │   └── WeatherPage.tsx        ← Weather + risk alerts
    │       │   └── utils/api.ts          ← All API calls with JWT
    │       └── package.json
    └── docs/
        ├── architecture-diagram.png
        ├── API_DOCUMENTATION.md
        ├── SYSTEM_ARCHITECTURE.md
        └── DATABASE_SCHEMA.md
```

---

## Quick Start

### Backend

```bash
cd kisansathi/backend
cp .env.example .env          # Add your API keys (WeatherAPI, Gemini, MongoDB)
pip install -r requirements.txt
python app_enhanced.py        # → http://localhost:5000
```

### Frontend

```bash
cd kisansathi/frontend/pixel-perfect-copy
cp .env.example .env          # Set VITE_API_URL=http://localhost:5000
npm install --legacy-peer-deps
npm run dev                   # → http://localhost:8080
```

### Linting

```bash
# Python backend
cd kisansathi/backend
ruff check .                  # or: flake8 .

# TypeScript frontend
cd kisansathi/frontend/pixel-perfect-copy
npm run lint
```

---

## API Quick Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | — | Register new farmer |
| POST | `/api/auth/login` | — | Login, returns JWT |
| GET/POST | `/api/farm-profile` | JWT | Get / create-update farm profile |
| GET | `/api/farm-profile/irrigation-advice` | JWT | Farm-specific ET₀ irrigation schedule |
| GET | `/api/farm-profile/health-logs` | JWT | Crop health observation history |
| GET | `/api/weather/{location}` | — | Live weather + 5-day forecast |
| GET | `/api/weather/{location}/alerts` | — | Weather risk alerts |
| POST | `/api/recommendations/crop` | — | XGBoost crop recommendation (NPK input) |
| POST | `/api/recommendations/advanced-crop` | — | Seasonal crop rec (month + location) |
| POST | `/api/disease-predict` | — | Multi-image plant disease detection |
| POST | `/api/fertilizer/recommend` | — | ML fertilizer recommendation |
| GET | `/api/market/prices` | — | All commodity prices (live + MSP) |
| GET | `/api/market/prices/{commodity}` | — | Single commodity price + trade advice |
| POST | `/api/chatbot/message` | — | AI farming chatbot (Gemini) |

Full reference: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

---

## ML Models

| Model | File | Algorithm | Training Data | Accuracy |
|---|---|---|---|---|
| Crop Recommendation | `crop_recommendation_model_xgboost_comprehensive.pkl` | XGBoost | 2,200 samples, 22 crops | 97.3% |
| Fertilizer Recommendation | `fertilizer_model_xgboost.pkl` | XGBoost | NPK + soil + crop | ~100% |
| Soil Analysis | `soil_crop_recommendation_model.pkl` | Random Forest | Soil sensor data | 90%+ |
| Disease Detection | `disease_detection_model_xgboost_comprehensive.pkl` | XGBoost + PCA | PlantVillage features | 85%+ |
| Plant Disease (image) | `plant_disease_model.pth` | ResNet50 fine-tuned | PlantVillage images | 88%+ |
| Seasonal Crop | `seasonal_crop_model.pkl` | Random Forest | Season + NPK data | 88%+ |

---

## Security

- `.env` files are **gitignored** — never committed
- All secrets loaded via `os.getenv()` from environment variables
- Passwords hashed with **bcrypt** (salt rounds = 12)
- JWT tokens with 30-day expiry
- Rate limiting: 200 req/day, 50 req/hour per IP (Flask-Limiter)
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `HSTS`, `CSP`
- Input validation on all endpoints (`utils/input_validator.py`)

---

## Team

| Member | Role | Contributions |
|---|---|---|
| **Shivam Jaiswal** | Backend + ML | Flask API, ML model training, disease detection |
| **Bhoomi Kesharwani** | Backend + Weather | Weather integration, irrigation engine, farm profile API |
| **Sumit Dangi** | Frontend + Integration | React UI, dashboard, error handling, API integration |
| **Rustam Ali** | Security + Auth + DevOps | bcrypt auth, input validation, market prices module, linting |

---

## License

[MIT](LICENSE) — KisanSathi, HackInMotion 2026

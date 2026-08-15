# KisanSathi — Smart Farm Decision Support System

> HackInMotion 2026 | Theme: Agriculture & Farming | Team: **RICR-HIM-1054**

[![Theme](https://img.shields.io/badge/Theme-Agriculture_%26_Farming-green)](https://hackinmotion.in)
[![Stack](https://img.shields.io/badge/Stack-React_18_%7C_Flask_%7C_MongoDB_%7C_XGBoost-blue)](#)
[![License](https://img.shields.io/badge/License-MIT-yellow)](kisansathi/LICENSE)
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://kisansathi-frontend.vercel.app/)

**🌐 Live Demo:** [kisansathi-frontend.vercel.app](https://kisansathi-frontend.vercel.app/)

A full-stack Smart Farm Decision Support System that gives every farmer a data-driven advisor — combining live weather, ML crop/disease intelligence, and real mandi prices in one unified dashboard.

## 🔑 Demo Credentials

Use the following demo account to log in and test the deployed application (no need to register):

- **Mobile:** 7869037289
- **Password:** 212006

> ⚠️ Backend is hosted on Render's free tier — the first request after inactivity may take 30–50 seconds to respond (cold start). Please wait before assuming it's not working.

## Project Documentation

→ **[kisansathi/README.md](kisansathi/README.md)** — Full documentation, API reference, architecture, and setup guide.

## Quick Start

```bash
# Backend
cd kisansathi/backend
cp .env.example .env
pip install -r requirements.txt
python app_enhanced.py

# Frontend
cd kisansathi/frontend/pixel-perfect-copy
npm install --legacy-peer-deps
npm run dev
```

## Key APIs Used

| API | Purpose | Docs |
|---|---|---|
| [WeatherAPI.com](https://www.weatherapi.com/) | Live weather + forecast for irrigation engine | [Integration](kisansathi/backend/utils/weather_integration.py) |
| [AGMARKNET / data.gov.in](https://data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070) | Live mandi commodity prices | [Integration](kisansathi/backend/utils/market_prices.py) |
| [Google Gemini 2.5 Flash](https://ai.google.dev/) | Crop advice (Hindi), soil OCR | [Backend](kisansathi/backend/app_enhanced.py) |

## Team — RICR-HIM-1054

| Member | Role |
|---|---|
| Shivam Jaiswal | Backend + ML Models |
| Bhoomi Kesharwani | Backend + Weather Integration |
| Sumit Dangi | Frontend + Integration |
| Rustam Ali | Security + Auth + DevOps |

## Deliverables

| Deliverable | Location |
|---|---|
| Live Demo | [kisansathi-frontend.vercel.app](https://kisansathi-frontend.vercel.app/) |
| Architecture Diagram | [kisansathi/docs/architecture-diagram.png](kisansathi/docs/architecture-diagram.png) |
| API Documentation | [kisansathi/docs/API_DOCUMENTATION.md](kisansathi/docs/API_DOCUMENTATION.md) |
| Full README | [kisansathi/README.md](kisansathi/README.md) |

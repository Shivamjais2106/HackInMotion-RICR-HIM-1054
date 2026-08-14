# 🏗️ KisanSathi - Complete System Architecture (`SYSTEM_ARCHITECTURE.md`)

This document details the software architecture, mathematical decision models, and data pipeline powering **KisanSathi** (HackInMotion 2026 | `RICR-HIM-1054`).

---

## 📐 End-to-End System Architecture

![Architecture Diagram](../architecture-diagram.png)

```
+-----------------------------------------------------------------------------------+
|                            PRESENTATION LAYER (Frontend)                         |
|   React 18 + Vite + TypeScript + Tailwind CSS + Lucide Icons + Recharts Analytics |
|   [ Unified Command Center | Farm Profile Modal | Irrigation Card | Mandi Feed ]   |
+----------------------------------------+------------------------------------------+
                                         | HTTP REST & SocketIO WebSockets
                                         v
+-----------------------------------------------------------------------------------+
|                        APPLICATION & DECISION LAYER (Backend)                     |
|   Flask Python Engine + JWT Middleware + Rate Limiter + Celery Task Queue         |
|   • Farm Profile Manager (/api/farm/profile)                                      |
|   • Evapotranspiration Calculator (ET0 Hargreaves Radiation Model)               |
|   • Microclimate Pest Hazard Matrix (Humidity/Temp Rule Diagnostic Engine)        |
|   • Mandi Commodity Feed & Trend Engine (/api/farm/decision/mandi-prices)         |
+-------------------+--------------------+--------------------+---------------------+
                    |                    |                    |
                    v                    v                    v
+-----------------------+ +------------------+ +----------------------------------+
|    DATA PERSISTENCE   | |  IN-MEMORY CACHE | |        EXTERNAL SERVICES         |
|   MongoDB Database    | |   Redis Cache    | | • OpenWeather API                |
|   (Profiles, Logs)    | |  (Sessions/ET)   | | • Google Gemini 2.5 AI Vision  |
+-----------------------+ +------------------+ +----------------------------------+
```

---

## 🧮 Decision Support Engine Mathematical Formulations

### 1. Reference Evapotranspiration ($ET_0$) Formula (Hargreaves Equation)
$$ET_0 = 0.0023 \times R_a \times (T_{\text{mean}} + 17.8) \times \sqrt{T_{\text{max}} - T_{\text{min}}}$$

Where:
- $R_a$: Extraterrestrial radiation in mm/day derived from solar declination and latitude ($\phi$).
- $T_{\text{max}}, T_{\text{min}}, T_{\text{mean}}$: Maximum, minimum, and mean daily temperature (°C).

### 2. Crop Water Requirement ($ET_c$) Formula
$$ET_c = ET_0 \times K_c$$
$$\text{Net Irrigation Depth (mm)} = \max(0, ET_c - 0.7 \times \text{Rainfall})$$
$$\text{Total Water Volume (Liters)} = \text{Net Depth (mm)} \times 4046.86 \times \text{Acres} \times \text{Soil Multiplier}$$
$$\text{Pump Runtime (Hours)} = \frac{\text{Total Water Volume (L)}}{P_{\text{flow}} \text{ (LPH)}}$$

---

## 🔐 Security & Reliability Layer
- **Token Security**: 256-bit HMAC JWT tokens with 30-day expiration.
- **Secrets Management**: Untracked `.env` files; `.gitignore` enforced against secrets and bytecode.
- **Failover Logic**: Local fallback decision payloads if weather or Mandi APIs experience downtime.

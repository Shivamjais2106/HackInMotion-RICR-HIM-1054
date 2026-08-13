# 📜 KisanSathi - Complete Project Changelog (`CHANGELOG.md`)

All notable changes, architectural updates, and audit remediation milestones for **KisanSathi** (HackInMotion 2026 | `RICR-HIM-1054`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [5.0.0-HIM-1054] - 2026-08-14 (HackInMotion Pre-qualifier Competition Upgrade)

### 🌾 Smart Farm Decision Support Engine (Core Problem Statement Alignment)
- **Persistent Farm Profile Entity**: Created `/api/farm/profile` (GET, POST) supporting land size (acres), soil texture (Loam, Clay, Sandy, Silt), soil pH, crop rotations, and pump capacity.
- **Hargreaves Evapotranspiration ($ET_0$) Irrigation Calculator**: Built mathematical radiation & crop coefficient ($K_c$) water requirement engine calculating daily volume in Liters/Acre and motor pump run hours.
- **Microclimate Pest & Hazard Threat Matrix**: Implemented relative humidity & temperature rule matrix detecting Fungal Late Blight, Frost risk, Heat stress, and Aphids.
- **Live APMC Mandi Price Intelligence**: Real-time commodity rate feed (`/api/farm/decision/mandi-prices`) with 7-day historical price points and trade advisories.
- **Unified Farmer Command Center Dashboard**: Redesigned `DashboardEnhanced.tsx` into a real-time command center with interactive Recharts commodity price trend graphs.
- **Farm Observation Logs**: Connected AI plant disease scans directly to the active farmer profile (`/api/farm/observation-logs`).

### 🛡️ Security Hardening & Git Hygiene
- Untracked sensitive `.env` and `.env.production` files from Git index.
- Applied comprehensive root `.gitignore` filtering out bytecode (`__pycache__`), virtual environments (`venv/`), and node modules.

### 📄 Mandatory Submission Deliverables Suite
- Generated `architecture-diagram.png` (High-res system visual).
- Created `api-documentation.md` (25+ REST & WebSocket endpoint specifications).
- Created `presentation.pptx` (PowerPoint presentation deck).
- Created complete documentation suite inside `docs/` repository path (`API_DOCUMENTATION.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `DATABASE_SCHEMA.md`, `DEVELOPMENT_ROADMAP.md`, `PRODUCT_REQUIREMENTS.md`, `SYSTEM_ARCHITECTURE.md`, `UI_UX_GUIDELINES.md`).

---

## [4.0.0] - 2026-08-12 (Multi-Model Backend & Vision OCR Release)
- Integrated Google Gemini 2.5 Vision for plant disease diagnosis and soil report OCR parsing.
- Implemented JWT authentication and rate limiting middleware in Flask backend.
- Integrated SocketIO for real-time community chat and monitoring events.

---

## [1.0.0] - 2026-08-01 (Prototype Initialization)
- Basic Vite + React 18 + Tailwind CSS frontend boilerplate setup.
- Weather API integration and shop page layout prototype.

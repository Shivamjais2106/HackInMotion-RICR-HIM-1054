# KisanSathi Frontend

React 18 + TypeScript + Vite frontend for the KisanSathi Smart Farm Decision Support System.

## Tech Stack

- **React 18** + TypeScript
- **Vite 8** (build tool)
- **TailwindCSS** + shadcn/ui (styling)
- **React Router** (navigation)
- **JWT** authentication via localStorage

## Setup

```bash
# Install dependencies
npm install --legacy-peer-deps

# Copy env template
cp .env.example .env

# Start dev server
npm run dev        # http://localhost:8080
```

## Environment Variables

```env
VITE_API_URL=http://localhost:5000
```

## Pages

| Route | Page | Description |
|---|---|---|
| `/` | Index | Landing page |
| `/auth` | AuthPage | Login / Register |
| `/dashboard` | DashboardEnhanced | Unified farm dashboard |
| `/farm-profile` | FarmProfilePage | Farm setup and profile |
| `/crop` | CropCompletePage | ML crop recommendation |
| `/disease` | DiseasePage | Plant disease detection |
| `/fertilizer` | FertilizerPage | Fertilizer recommendation |
| `/soil-analysis` | SoilAnalysisPage | Soil analysis |
| `/weather` | WeatherPage | Weather + irrigation advice |
| `/market` | MarketPricePage | Mandi prices, MSP and sell/hold advisory |
| `/shop` | ShopPage | Farm inputs + live mandi prices |
| `/community` | CommunityPage | Farmer groups |
| `/livestock` | LivestockPage | Livestock health |
| `/reminders` | SmartRemindersPage | Crop reminders |
| `/chatbot` | ChatbotPage | AI assistant |

## Build

```bash
npm run build      # Production build → dist/
npm run lint       # ESLint check
npm run preview    # Preview production build
```

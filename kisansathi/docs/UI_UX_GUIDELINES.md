# 🎨 KisanSathi - Enterprise UI / UX Design Guidelines (`UI_UX_GUIDELINES.md`)

This document defines the **Design System**, UI tokens, color palettes, responsive typography, and accessibility standards for **KisanSathi**.

---

## 🎨 Color Palette & Tokens

- **Primary Brand Color**: Emerald Green (`#10b981` / `bg-emerald-600`) - Represents growth, farming, and health.
- **Secondary Accent**: Blue & Cyan (`#3b82f6` / `#06b6d4`) - Represents smart irrigation, water, and weather.
- **Warning & Hazard**: Amber & Orange (`#f59e0b` / `#ea580c`) - Represents microclimate risk alerts.
- **Critical Alert**: Red (`#ef4444`) - Represents severe crop heat stress or frost warnings.
- **Background**: Slate Gradient (`from-slate-50 to-slate-100` / `#0f172a` for dark command headers).

---

## 🧩 UI Components & Data Visualizations

### 1. Recharts Commodity Price Trend Chart
- **Library**: `recharts` (`AreaChart`, `Area`, `XAxis`, `YAxis`, `Tooltip`)
- **Stroke**: Emerald `#059669` (Width 2.5px)
- **Gradient Fill**: Emerald opacity gradient from 0.4 to 0.0

### 2. Decision Status Badges
- **Irrigate Required**: `bg-blue-600 text-white`
- **Rain Saturated**: `bg-emerald-600 text-white`
- **High Risk Hazard**: `bg-red-600 text-white`

---

## 📱 Outdoor Accessibility Standards
1. **High Contrast Ratio**: Minimum 4.5:1 contrast for outdoor sunlight readability.
2. **Touch Target Dimensions**: Minimum 44x44px target area for all buttons and interactive cards.
3. **Bilingual Toggle**: Support English and Hindi (`useLanguage` context hook).

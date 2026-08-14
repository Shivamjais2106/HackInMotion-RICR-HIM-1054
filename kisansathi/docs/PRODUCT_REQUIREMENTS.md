# 📋 KisanSathi - Product Requirements Document (`PRODUCT_REQUIREMENTS.md`)

## 1. Problem Statement & Background
Smallholder farmers in India lack hyper-local, farm-scoped decision intelligence. Standard weather forecasts report generic city temperature without computing exact daily irrigation water requirements (Liters/Acre) or identifying microclimate disease threats, leading to water wastage, crop loss, and distress Mandi sales.

---

## 2. Target User Personas

### Persona A: Smallholder Grain Farmer (Ramesh)
- **Land**: 5 Acres in Karnal, Haryana.
- **Crops**: Wheat (Rabi season), Paddy (Kharif season).
- **Pain Point**: Over-irrigates fields due to lack of evapotranspiration knowledge, causing high electricity bills and root rot.

### Persona B: Progressive Vegetable Grower (Sunita)
- **Land**: 3 Acres in Nashik, Maharashtra.
- **Crops**: Tomato & Chili.
- **Pain Point**: Sudden Fungal Late Blight outbreaks destroying 40% yield before detection.

---

## 3. Key Functional Requirements Matrix

| Requirement ID | Module | Functional Specification | Verification Test | Status |
| :--- | :--- | :--- | :--- | :---: |
| **FR-1.1** | Farm Profile | System shall persist land size (acres), soil type, pH, crops, and pump LPH. | Profile CRUD Unit Test | ✅ Implemented |
| **FR-2.1** | Irrigation Engine | System shall calculate Hargreaves $ET_0$ and output pump runtime hours. | ET0 Algorithm Calculation Test | ✅ Implemented |
| **FR-3.1** | Climate Risk Matrix | System shall trigger alerts for Fungal Blight when humidity >=74%. | Weather Risk Diagnostic Test | ✅ Implemented |
| **FR-4.1** | Mandi Intelligence | System shall render APMC rates with 7-day trend chart and sell advisory. | Mandi API Response Test | ✅ Implemented |
| **FR-5.1** | AI Vision Scan | System shall diagnose plant diseases from leaf photos with remedy steps. | Vision Inference Test | ✅ Implemented |
| **FR-6.1** | Command Hub | Unified React dashboard integrating all 4 core decision tiles. | Frontend Build (`npm run build`) | ✅ Implemented |

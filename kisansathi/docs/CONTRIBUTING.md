# 🤝 Contributing to KisanSathi (`CONTRIBUTING.md`)

Thank you for your interest in contributing to **KisanSathi - Smart Farm Decision Support System** (Project: `RICR-HIM-1054`).  
This document outlines our engineering guidelines, pull request submission standards, code styling rules, and development practices.

---

## 🛠️ Code of Conduct & Core Engineering Principles

1. **Farmer-Centric Accessibility**: All UI components must be fully responsive, high contrast for outdoor visibility, and accessible on low-bandwidth rural connections.
2. **Strict Security Policies**: Never commit `.env` files, production database strings, or unhashed secrets.
3. **Deterministic Testing**: Verify all changes against frontend linter (`npm run lint`) and production build (`npm run build`).

---

## 🌿 Git Branching Strategy

We follow the **GitFlow** model:
- `main`: Production-ready release code.
- `develop`: Integration branch for active features.
- `feature/<feature-name>`: Short-lived feature branches.
- `fix/<bug-description>`: Bugfix branches.

```bash
# 1. Clone repository
git clone https://github.com/Shivamjais2106/kisansathi.git
cd kisansathi

# 2. Checkout feature branch
git checkout -b feature/smart-irrigation-enhancement
```

---

## 💻 Local Development Setup

### Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Run Flask backend
python app_enhanced.py
```

### Frontend Setup
```bash
cd frontend/pixel-perfect-copy
npm install
npm run dev
```

---

## 📋 Pull Request Submission Checklist

Before opening a PR to `main`:
- [ ] Code builds without errors (`npm run build`).
- [ ] No `.env` secrets or `__pycache__` committed.
- [ ] All new backend endpoints are documented in `docs/API_DOCUMENTATION.md`.

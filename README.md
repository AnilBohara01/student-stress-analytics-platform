# 🧠 StressLens — Student Stress Assessment & Lifestyle Analytics Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django" alt="Django">
  <img src="https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/XGBoost-2.0.0-EC6B23?style=for-the-badge&logo=xgboost" alt="XGBoost">
  <img src="https://img.shields.io/badge/SHAP-Explainable%20AI-4B0082?style=for-the-badge" alt="SHAP">
  <img src="https://img.shields.io/badge/ReportLab-PDF%20Engine-1E3A8A?style=for-the-badge" alt="ReportLab">
  <img src="https://img.shields.io/badge/Tests-Passing%20(100%25)-success?style=for-the-badge" alt="Tests">
</p>

---

## 📌 Executive Summary

**StressLens** is an end-to-end Machine Learning and Web Engineering platform designed for early risk identification, explainable prediction, and personalized lifestyle intervention in university students. 

Grounded in empirical data across **25,476 clean student records**, the platform evaluates key physiological, academic, and socio-environmental lifestyle metrics—such as sleep hours, study duration, exam pressure, attendance, and family support. It features a hyperparameter-tuned **XGBoost Classifier** (ROC-AUC **0.8756**, Accuracy **81.99%**), an **Explainable AI (SHAP)** tree-attribution engine, a dedicated **FastAPI Microservice**, a modern cream-white **Django Web Application**, and automated **PDF Report Generation**.

> ⚠️ **Academic Disclaimer**: *This platform is developed strictly for academic, educational, and research screening purposes. It delivers machine-learning-based risk indicators and does NOT constitute a clinical or psychiatric diagnosis.*

---

## 🌟 Key Features & Capabilities

- 🤖 **Machine Learning Predictive Engine:** Hyperparameter-tuned XGBoost model trained on 25,476 records with 80/20 stratified split.
- 💡 **Explainable AI (XAI) via SHAP:** Uses `TreeExplainer` to calculate exact feature attributions for every individual student assessment.
- ⚡ **FastAPI Microservice:** High-performance async REST API on Port `8001` with interactive **Swagger UI** (`/docs`) and **ReDoc** (`/redoc`).
- 🎨 **Modern Cream-White UX System:** Custom, human-designed frontend (`#FDFBF7`) built with responsive grid layouts, glassmorphism card highlights, and dynamic risk gauges.
- 🛡️ **Resilient Dual-Mode Architecture:** Django connects to FastAPI over HTTP with an **automatic zero-downtime failover** to direct local Python ML execution.
- 📄 **Dynamic PDF Report Generation:** Built-in ReportLab engine providing instant one-click download of official assessment summary reports.
- 📊 **Analytics Dashboard & History:** Comprehensive student dashboard with interactive Chart.js metrics, trend logging, and risk probability breakdowns.
- 🐳 **Docker & Container Ready:** Ships with `Dockerfile` and `docker-compose.yml` for simplified deployment.

---

## 🏗️ System Architecture

```text
+-------------------------------------------------------------------+
|                        User Browser / UI                          |
|    Cream-White Theme (#FDFBF7), Analytics Dashboard, Forms        |
+-------------------------------------------------------------------+
                                  │
                                  │ HTTP (Port 8000)
                                  ▼
+-------------------------------------------------------------------+
|                       Django Web Application                      |
|  Views, Auth, Models (User, Assessment), SQLite, PDF Generation   |
+-------------------------------------------------------------------+
                                  │
            ┌─────────────────────┴─────────────────────┐
            │ HTTP POST (Port 8001)                     │ Fallback (if offline)
            ▼                                           ▼
+-----------------------+                   +-----------------------+
|  FastAPI Microservice |                   | Local Python ML Engine|
| (fastapi_app/main.py) |                   | (ml/src/predict.py)   |
| XGBoost & SHAP Models |                   | XGBoost & SHAP Models |
+-----------------------+                   +-----------------------+
```

---

## 📊 Machine Learning Model Benchmarking

Six classifier architectures were benchmarked under 5-fold stratified cross-validation on an independent hold-out test set of 5,096 samples:

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Tuned XGBoost** | **81.99%** | **73.94%** | **61.65%** | **0.6724** | **0.8756** | 🟢 **Selected Production Model** |
| **Logistic Regression** | 82.16% | 74.43% | 61.71% | 0.6748 | 0.8744 | ⚪ Baseline Benchmark |
| **Random Forest** | 82.04% | 74.58% | 60.86% | 0.6703 | 0.8658 | ⚪ Ensemble Benchmark |
| **Baseline XGBoost** | 81.65% | 73.11% | 61.39% | 0.6674 | 0.8738 | ⚪ Untuned Benchmark |
| **Extra Trees Classifier** | 80.83% | 73.33% | 56.68% | 0.6394 | 0.8635 | ⚪ Alternative Tree |
| **Decision Tree** | 79.87% | 69.89% | 57.72% | 0.6323 | 0.8091 | ⚪ Single Tree Baseline |

---

## 🔌 FastAPI Endpoint Documentation

The FastAPI microservice runs on `http://127.0.0.1:8001` and exposes the following endpoints:

| Method | Endpoint | Description | Sample Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Service status metadata & API links | `{"service": "FastAPI Stress Microservice", "status": "online"}` |
| `GET` | `/health` | Health check verifying model pipeline | `{"status": "ok", "model_loaded": true}` |
| `POST` | `/api/v1/predict` | Generates stress risk prediction | `{"prediction_code": 1, "predicted_label": "High Stress"}` |
| `POST` | `/api/v1/explain` | Computes SHAP feature attributions | `{"top_contributing_factors": [...], "narrative_explanation": "..."}` |
| `POST` | `/api/v1/analyze` | Unified prediction + SHAP response | `{"prediction": {...}, "explanation": {...}, "status": "success"}` |

### Interactive Documentation
- **Swagger UI:** [`http://127.0.0.1:8001/docs`](http://127.0.0.1:8001/docs)
- **ReDoc:** [`http://127.0.0.1:8001/redoc`](http://127.0.0.1:8001/redoc)

---

## 📁 Repository Directory Hierarchy

```text
Django_Project/
├── config/                 # Root Django configuration & routing (settings.py, urls.py)
├── accounts/               # User authentication & registration app
├── assessments/            # Core assessment logic, database models, services & PDF reports
│   ├── models.py           # Assessment Django ORM model
│   ├── views.py            # Assessment HTTP request views
│   ├── services.py         # FastAPI HTTP client with local failover
│   ├── feedback.py         # Rule-based personalized lifestyle recommendation engine
│   └── reports.py          # ReportLab PDF synthesis engine
├── dashboard/              # Analytics dashboard views & Chart.js data formatting
├── fastapi_app/            # FastAPI ML Microservice package
│   ├── main.py             # FastAPI endpoints & CORS middleware
│   └── schemas.py          # Pydantic request/response validation models
├── ml/                     # Machine learning pipeline
│   ├── data/               # Raw & processed dataset (StressLevelDataset.csv)
│   ├── models/             # Serialized joblib pipeline artifacts (stresslens_v1.0.0.joblib)
│   ├── notebooks/          # Exploratory EDA & tuning notebooks
│   └── src/                # Modular scripts (train.py, predict.py, explain.py)
├── templates/              # Redesigned cream-white HTML5 templates
├── static/                 # Static assets (CSS, JS, Icons)
├── tests/                  # Automated unit test suite (Django, FastAPI, ML)
├── build_academic_report.py# Academic report PDF generator script
├── run_fastapi.py          # FastAPI service launcher script
├── manage.py               # Django CLI management script
├── Dockerfile              # Docker container manifest
├── docker-compose.yml      # Multi-container orchestration config
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

---

## 🚀 Quickstart Guide & Local Execution

### 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.12)
- Git

### 2. Installation & Setup

```bash
# Clone the repository
git clone https://github.com/anil-bohara/student-stress-analytics-platform.git
cd student-stress-analytics-platform

# Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create Django Admin Superuser (Optional)
python manage.py createsuperuser
```

### 3. Launching the Platform

To run the complete platform with both servers active:

#### Terminal 1: Launch FastAPI Microservice (Port 8001)
```bash
python run_fastapi.py
```

#### Terminal 2: Launch Django Web Server (Port 8000)
```bash
python manage.py runserver 8000
```

Open your browser and navigate to:
- **Django Application:** [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/)
- **FastAPI Documentation:** [`http://127.0.0.1:8001/docs`](http://127.0.0.1:8001/docs)

---

## 🧪 Running Automated Unit Tests

Execute the complete 100% test suite covering FastAPI endpoints, Django views, and ML models:

```bash
# Run FastAPI & ML Unit Tests
python -m unittest discover -s tests

# Run Django Web Unit Tests
python manage.py test
```

---

## 🐳 Docker Deployment

To launch the platform in a containerized environment:

```bash
# Build and start services using Docker Compose
docker-compose up --build
```

---

## 👤 Author & Acknowledgments

- **Author / Developer:** Anil Bohara (Student ID: 25126458)
- **Domain:** Computer Science & Software Engineering / Machine Learning & Web Analytics
- **Submission Date:** September 2026

*Crafted with Python, Django, FastAPI, XGBoost, SHAP, and ReportLab.*

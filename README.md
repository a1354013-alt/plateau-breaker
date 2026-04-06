# Plateau Breaker

A full-stack health tracking and weight plateau detection system built with **FastAPI** and **Vue 3**.  
This application helps users monitor daily fitness data, detect weight loss plateaus, analyze possible causes, and generate actionable insights through interactive dashboards.

---

# 📌 Project Overview

**Plateau Breaker** is a full-stack web application designed to help users track their daily health metrics and identify weight loss plateaus.

Instead of simply recording data, the system performs rule-based analysis on recent trends to detect:

- Weight plateau patterns
- Lifestyle-related causes
- Behavioral insights
- Actionable recommendations

This project demonstrates:

- Full-stack system design
- RESTful API architecture
- Data analysis logic
- State management
- Interactive data visualization

---

# 🧠 Core Features

## 📊 Health Data Tracking

Users can record daily health metrics:

- Weight
- Sleep Hours
- Calories
- Protein Intake
- Exercise Minutes
- Steps
- Notes

Supports:

- Create records
- Edit records
- Delete records
- Pagination and filtering

---

## 📉 Plateau Detection Engine

The system analyzes weight trends to detect plateaus.

Detection rules include:

- **Rule A:**  
  Compare average weight of recent 7 days vs previous 7 days

- **Rule B:**  
  Detect low fluctuation range over recent days

Possible outcomes:

- Plateau
- Losing weight
- Gaining weight
- Insufficient data

---

## 🔍 Cause Analysis

When a plateau is detected, the system evaluates:

- Sleep quality
- Calorie intake trends
- Weekend eating patterns
- Exercise consistency
- Data completeness

Top causes are ranked by severity.

---

## 💡 Insight Generation

The system generates:

- Status summaries
- Behavioral insights
- Suggested actions

Example:

- Increase sleep consistency
- Reduce calorie intake
- Maintain exercise routine

---

## 📈 Interactive Dashboard

Includes:

- KPI summary cards
- Weight trend charts
- Sleep charts
- Calorie charts
- Plateau alerts

Built using:

- Chart.js
- PrimeVue UI components

---

# 🏗️ System Architecture
Frontend (Vue 3)
|
| REST API
|
Backend (FastAPI)
|
| ORM
|
Database (SQLite)


---

# 🧰 Tech Stack

## Backend

- FastAPI
- SQLModel
- SQLite
- Pydantic
- Python

## Frontend

- Vue 3
- Vite
- Pinia
- PrimeVue
- Chart.js
- Axios

## Development Tools

- TypeScript
- ESLint
- Prettier

---

# 📂 Project Structure
PlateauBreaker/

├── backend/
│ ├── app/
│ │ ├── main.py
│ │ ├── models/
│ │ ├── schemas/
│ │ ├── routers/
│ │ ├── services/
│ │ └── rules/
│ │
│ └── requirements.txt
│
├── frontend/
│ ├── src/
│ │ ├── views/
│ │ ├── stores/
│ │ ├── services/
│ │ └── components/
│ │
│ └── package.json
│
└── README.md

---

# 🚀 Getting Started

## 1️⃣ Clone Repository

```bash
git clone https://github.com/a1354013-alt/plateau-breaker

cd plateau-breaker


---

# 🚀 Getting Started

## 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/plateau-breaker.git

cd plateau-breaker

cd backend

python -m venv venv

venv\Scripts\activate     # Windows

pip install -r requirements.txt

uvicorn app.main:app --reload

Backend runs at:

http://localhost:8000

API docs:

http://localhost:8000/docs

🧩 Key Engineering Highlights

This project demonstrates:

Full-Stack Integration
Vue 3 frontend
FastAPI backend
RESTful communication
Shared data models
Rule-Based Analytics Engine

Includes:

Plateau detection logic
Cause ranking system
Insight generation

This simulates real-world analytical workflows.

State Management Design

Uses:

Pinia store architecture
Centralized analytics state
Computed helpers

Ensures UI consistency.

Modular Backend Design

Separated into:

Models
Schemas
Services
Rules

This improves:

Maintainability
Scalability
Testability
📈 Future Improvements

Potential upgrades:

Machine learning-based plateau prediction
User authentication system
Cloud database support
Docker deployment
Mobile UI support
Personalized recommendations
🧠 Why This Project Matters

Weight plateaus are a common challenge in fitness tracking.

This system demonstrates how software engineering and data logic can be combined to:

Detect behavioral patterns
Identify root causes
Provide actionable insights

It showcases practical full-stack engineering skills beyond CRUD applications.

📄 License

MIT License


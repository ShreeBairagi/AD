# ADP Project

## Setup and Run Instructions

Follow these exact commands to start the databases, API, and UI.

### 1. Start Databases (Docker)
```bash
docker-compose up -d
```

### 2. Setup Python Environment
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start the API (FastAPI)
Run this locally (not in Docker) in a new terminal with the virtual environment activated:
```bash
uvicorn api.main:app --reload
```

### 4. Start the UI (Streamlit)
Run this locally in another new terminal with the virtual environment activated:
```bash
streamlit run ui/app.py
```

@echo off
echo Starting Bill Tracker Backend...

cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if database exists, if not initialize with sample data
if not exist "bill_tracker.db" (
    echo Database not found. Initializing with sample data...
    python init_sample_data.py
)

REM Start the server
echo Starting FastAPI server on http://localhost:8000
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

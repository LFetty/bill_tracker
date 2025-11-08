#!/bin/bash

echo "Starting Bill Tracker Backend..."

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if database exists
if [ ! -f "bill_tracker.db" ]; then
    echo "Database not found. Initializing with sample data..."
    python init_sample_data.py
else
    echo "Running database migration (if needed)..."
    python migrate_db.py
fi

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

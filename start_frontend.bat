@echo off
echo Starting Bill Tracker Frontend...

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Node modules not found. Installing...
    npm install
)

REM Start the development server
echo Starting Vite dev server on http://localhost:3000
npm run dev

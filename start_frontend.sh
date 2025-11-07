#!/bin/bash

echo "Starting Bill Tracker Frontend..."

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Node modules not found. Installing..."
    npm install
fi

# Start the development server
echo "Starting Vite dev server on http://localhost:3000"
npm run dev

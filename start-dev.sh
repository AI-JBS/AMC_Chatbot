#!/bin/bash

echo "Starting Asset Management Chatbot Development Environment..."
echo

# Check if backend virtual environment exists
if [ ! -d "back-end/.venv" ]; then
    echo "ERROR: Virtual environment not found at back-end/.venv"
    echo "Please create virtual environment first:"
    echo "cd back-end"
    echo "python -m venv .venv"
    echo "source .venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Check if frontend node_modules exists
if [ ! -d "front-end/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd front-end
    npm install
    cd ..
fi

echo "Starting Backend Server..."
cd back-end
gnome-terminal --title="Backend Server" -- bash -c "source .venv/bin/activate && python main.py; exec bash" &
cd ..

echo "Waiting for backend to start..."
sleep 5

echo "Starting Frontend Server..."
cd front-end
gnome-terminal --title="Frontend Server" -- bash -c "npm run dev; exec bash" &
cd ..

echo
echo "==================================================="
echo "  Asset Management Chatbot is starting..."
echo "==================================================="
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo "==================================================="
echo
echo "Both servers are starting in separate terminals."
echo "Use Ctrl+C in each terminal to stop the servers."
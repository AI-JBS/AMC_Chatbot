@echo off
echo Starting Asset Management Chatbot Development Environment...
echo.

REM Check if backend virtual environment exists
if not exist "back-end\.venv" (
    echo ERROR: Virtual environment not found at back-end\.venv
    echo Please create virtual environment first:
    echo cd back-end
    echo python -m venv .venv
    echo .venv\Scripts\activate
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if frontend node_modules exists
if not exist "front-end\node_modules" (
    echo Installing frontend dependencies...
    cd front-end
    call npm install
    cd ..
)

echo Starting Backend Server...
cd back-end
start cmd /k ".venv\Scripts\activate && python main.py"
cd ..

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
cd front-end
start cmd /k "npm run dev"
cd ..

echo.
echo ===================================================
echo   Asset Management Chatbot is starting...
echo ===================================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo ===================================================
echo.
echo Both servers are starting in separate windows.
echo Close this window after servers are running.
pause
@echo off
REM UDCPR Master - Local Startup Script for Windows
REM This script starts all services locally

echo ========================================
echo    UDCPR MASTER - LOCAL STARTUP
echo ========================================
echo.

REM Check if MongoDB is running
echo [1/7] Checking MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] MongoDB is running
) else (
    echo [!] MongoDB is not running
    echo Please start MongoDB first:
    echo   - Run "mongod" in a separate terminal
    echo   - Or start MongoDB service
    echo.
    pause
    exit /b 1
)

echo.
echo [2/7] Starting Backend API (Node.js)...
echo Port: 5000
start "UDCPR Backend" cmd /k "cd backend && npm start"
timeout /t 3 >nul

echo.
echo [3/7] Starting Rule Engine API (Python)...
echo Port: 5001
start "UDCPR Rule Engine" cmd /k "cd rule_engine && python api_service.py"
timeout /t 3 >nul

echo.
echo [4/7] Starting RAG Service (AI Assistant)...
echo Port: 8000
start "UDCPR RAG Service" cmd /k "cd ai_services && python rag_service.py"
timeout /t 3 >nul

echo.
echo [5/7] Starting Vision Service...
echo Port: 8001
start "UDCPR Vision Service" cmd /k "cd vision && python vision_api.py"
timeout /t 3 >nul

echo.
echo [6/7] Starting Frontend (React)...
echo Port: 3000
start "UDCPR Frontend" cmd /k "cd frontend && npm start"
timeout /t 3 >nul

echo.
echo [7/7] All services starting...
echo.
echo ========================================
echo    SERVICES STARTED
echo ========================================
echo.
echo Frontend:      http://localhost:3000
echo Backend API:   http://localhost:5000
echo Rule Engine:   http://localhost:5001
echo RAG Service:   http://localhost:8000
echo Vision Service: http://localhost:8001
echo MongoDB:       mongodb://localhost:27017
echo.
echo Press Ctrl+C in each window to stop services
echo ========================================
echo.
pause

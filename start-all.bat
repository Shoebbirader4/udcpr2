@echo off
echo ========================================
echo    UDCPR MASTER - STARTING ALL SERVICES
echo ========================================
echo.

REM Check if MongoDB is running
echo [1/6] Checking MongoDB...
sc query MongoDB | find "RUNNING" >nul
if %errorlevel% equ 0 (
    echo     MongoDB is already running
) else (
    echo     Starting MongoDB...
    net start MongoDB
    timeout /t 3 >nul
)

echo.
echo [2/6] Starting Backend API (Port 5000)...
start "Backend API" cmd /k "cd backend && npm start"
timeout /t 3 >nul

echo [3/6] Starting Rule Engine (Port 5001)...
start "Rule Engine" cmd /k "cd rule_engine && python api_service.py"
timeout /t 3 >nul

echo [4/6] Starting RAG Service (Port 8002)...
start "RAG Service" cmd /k "cd ai_services && python rag_service.py"
timeout /t 3 >nul

echo [5/6] Starting Vision Service (Port 8001)...
start "Vision Service" cmd /k "cd vision && python vision_api.py"
timeout /t 3 >nul

echo [6/6] Starting Frontend (Port 3000)...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo    ALL SERVICES STARTING!
echo ========================================
echo.
echo Services will open in separate windows.
echo Wait 30-60 seconds for all services to start.
echo.
echo Then open: http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul

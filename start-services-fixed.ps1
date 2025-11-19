# UDCPR Master - Fixed Auto Start Script
# Handles port conflicts and missing dependencies

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   UDCPR MASTER - STARTING SERVICES" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Check MongoDB
Write-Host "Step 1: Checking MongoDB..." -ForegroundColor Yellow
$mongoCheck = Get-Process mongod -ErrorAction SilentlyContinue
if ($mongoCheck) {
    Write-Host "✅ MongoDB is running (PID: $($mongoCheck.Id))" -ForegroundColor Green
} else {
    Write-Host "⚠️  MongoDB not running" -ForegroundColor Yellow
    Write-Host "`nPlease start MongoDB using ONE of these methods:" -ForegroundColor White
    Write-Host "  1. Windows Service: " -NoNewline; Write-Host "net start MongoDB" -ForegroundColor Cyan
    Write-Host "  2. Local Install:   " -NoNewline; Write-Host "mongod" -ForegroundColor Cyan
    Write-Host "  3. Docker:          " -NoNewline; Write-Host "docker run -d -p 27017:27017 --name udcpr-mongodb mongo:7.0" -ForegroundColor Cyan
    Write-Host "`nPress any key after starting MongoDB..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

Write-Host "`nStep 2: Starting Backend Services...`n" -ForegroundColor Yellow

# Kill any processes on our ports
Write-Host "Checking for port conflicts..." -ForegroundColor Gray
$ports = @(5000, 5001, 8000, 8001, 3000)
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "  Stopping process on port $port ($($process.Name))..." -ForegroundColor Gray
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 500
        }
    }
}

# Start Backend API (Port 5000)
Write-Host "1️⃣  Starting Backend API (Port 5000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host '=== BACKEND API - Port 5000 ===' -ForegroundColor Green; npm start"
Start-Sleep -Seconds 3

# Start Rule Engine (Port 5001) - FIXED PORT
Write-Host "2️⃣  Starting Rule Engine (Port 5001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\rule_engine'; Write-Host '=== RULE ENGINE - Port 5001 ===' -ForegroundColor Green; python api_service.py"
Start-Sleep -Seconds 3

# Start RAG Service (Port 8000)
Write-Host "3️⃣  Starting RAG Service (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\ai_services'; Write-Host '=== RAG SERVICE - Port 8000 ===' -ForegroundColor Green; python rag_service.py"
Start-Sleep -Seconds 3

# Start Vision Service (Port 8001)
Write-Host "4️⃣  Starting Vision Service (Port 8001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\vision'; Write-Host '=== VISION SERVICE - Port 8001 ===' -ForegroundColor Green; python vision_api.py"
Start-Sleep -Seconds 3

# Start Frontend (Port 3000)
Write-Host "5️⃣  Starting Frontend (Port 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host '=== FRONTEND - Port 3000 ===' -ForegroundColor Green; npm start"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   ALL SERVICES STARTING!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Service URLs:" -ForegroundColor Yellow
Write-Host "  Frontend:       " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend API:    " -NoNewline; Write-Host "http://localhost:5000" -ForegroundColor Cyan
Write-Host "  Rule Engine:    " -NoNewline; Write-Host "http://localhost:5001" -ForegroundColor Cyan
Write-Host "  RAG Service:    " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Vision Service: " -NoNewline; Write-Host "http://localhost:8001" -ForegroundColor Cyan
Write-Host "  MongoDB:        " -NoNewline; Write-Host "mongodb://localhost:27017" -ForegroundColor Cyan

Write-Host "`n⏳ Wait 30-60 seconds for all services to start..." -ForegroundColor Yellow
Write-Host "🌐 Then open: " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Cyan -BackgroundColor DarkBlue

Write-Host "`n💡 Tip: Check each terminal window for startup messages" -ForegroundColor Gray
Write-Host "💡 Tip: Press Ctrl+C in any window to stop that service" -ForegroundColor Gray

Write-Host "`nPress any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

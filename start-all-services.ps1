# UDCPR Master - Auto Start All Services
# This script opens each service in its own terminal window

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   UDCPR MASTER - AUTO STARTUP" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if MongoDB is running
Write-Host "Checking MongoDB..." -ForegroundColor Yellow
$mongoCheck = netstat -an | Select-String "27017"
if ($mongoCheck) {
    Write-Host "✅ MongoDB is already running" -ForegroundColor Green
} else {
    Write-Host "⚠️  MongoDB not detected. Starting with Docker..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "docker run --rm -p 27017:27017 --name udcpr-mongodb mongo:7.0"
    Write-Host "Waiting 5 seconds for MongoDB to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

Write-Host "`nStarting services in separate windows...`n" -ForegroundColor Cyan

# Start Backend API (Port 5000)
Write-Host "1️⃣  Starting Backend API (Port 5000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; Write-Host 'BACKEND API - Port 5000' -ForegroundColor Green; npm start"
Start-Sleep -Seconds 2

# Start Rule Engine (Port 5001)
Write-Host "2️⃣  Starting Rule Engine (Port 5001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd rule_engine; Write-Host 'RULE ENGINE - Port 5001' -ForegroundColor Green; python api_service.py"
Start-Sleep -Seconds 2

# Start RAG Service (Port 8000)
Write-Host "3️⃣  Starting RAG Service (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ai_services; Write-Host 'RAG SERVICE - Port 8000' -ForegroundColor Green; python rag_service.py"
Start-Sleep -Seconds 2

# Start Vision Service (Port 8001)
Write-Host "4️⃣  Starting Vision Service (Port 8001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd vision; Write-Host 'VISION SERVICE - Port 8001' -ForegroundColor Green; python vision_api.py"
Start-Sleep -Seconds 2

# Start Frontend (Port 3000)
Write-Host "5️⃣  Starting Frontend (Port 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; Write-Host 'FRONTEND - Port 3000' -ForegroundColor Green; npm start"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   ALL SERVICES STARTING!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Service URLs:" -ForegroundColor Yellow
Write-Host "  Frontend:       http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API:    http://localhost:5000" -ForegroundColor White
Write-Host "  Rule Engine:    http://localhost:5001" -ForegroundColor White
Write-Host "  RAG Service:    http://localhost:8000" -ForegroundColor White
Write-Host "  Vision Service: http://localhost:8001" -ForegroundColor White
Write-Host "  MongoDB:        mongodb://localhost:27017" -ForegroundColor White

Write-Host "`nWait 30-60 seconds for all services to start..." -ForegroundColor Yellow
Write-Host "Then open: http://localhost:3000`n" -ForegroundColor Cyan

Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

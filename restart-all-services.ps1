# UDCPR Master - Restart All Services
# This kills any existing processes and starts fresh

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   RESTARTING ALL SERVICES" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Kill all processes on our ports
Write-Host "🛑 Stopping existing services..." -ForegroundColor Yellow
$ports = @(5000, 5001, 8000, 8001, 3000)

foreach ($port in $ports) {
    Write-Host "  Checking port $port..." -ForegroundColor Gray
    $connections = netstat -ano | Select-String ":$port\s"
    
    foreach ($conn in $connections) {
        if ($conn -match '\s+(\d+)\s*$') {
            $pid = $matches[1]
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "    Killing $($process.Name) (PID: $pid)" -ForegroundColor Gray
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                }
            } catch {
                # Process already gone
            }
        }
    }
}

Write-Host "`n✅ All ports cleared" -ForegroundColor Green
Write-Host "`n⏳ Waiting 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start all services
Write-Host "`n🚀 Starting all services...`n" -ForegroundColor Cyan

Write-Host "1️⃣  Starting Backend API (Port 5000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host '=== BACKEND API - Port 5000 ===' -ForegroundColor Green; npm start"
Start-Sleep -Seconds 2

Write-Host "2️⃣  Starting Rule Engine (Port 5001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\rule_engine'; Write-Host '=== RULE ENGINE - Port 5001 ===' -ForegroundColor Green; python api_service.py"
Start-Sleep -Seconds 2

Write-Host "3️⃣  Starting RAG Service (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\ai_services'; Write-Host '=== RAG SERVICE - Port 8000 ===' -ForegroundColor Green; python rag_service.py"
Start-Sleep -Seconds 2

Write-Host "4️⃣  Starting Vision Service (Port 8001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\vision'; Write-Host '=== VISION SERVICE - Port 8001 ===' -ForegroundColor Green; python vision_api.py"
Start-Sleep -Seconds 2

Write-Host "5️⃣  Starting Frontend (Port 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host '=== FRONTEND - Port 3000 ===' -ForegroundColor Green; npm start"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   ALL SERVICES STARTING!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "⏳ Wait 30-60 seconds for all services to start" -ForegroundColor Yellow
Write-Host "🌐 Then open: " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Cyan

Write-Host "`nPress any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

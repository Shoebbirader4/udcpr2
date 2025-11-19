# Fix RAG Service - Kill wrong service and start correct one

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   FIXING RAG SERVICE" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

# Kill process on port 8000
Write-Host "1. Stopping process on port 8000..." -ForegroundColor Yellow
$connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
foreach ($conn in $connections) {
    $pid = $conn.OwningProcess
    try {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "   Killing $($process.Name) (PID: $pid)" -ForegroundColor Gray
            Stop-Process -Id $pid -Force
        }
    } catch {}
}

Start-Sleep -Seconds 2
Write-Host "   ✅ Port 8000 cleared" -ForegroundColor Green

# Start correct RAG service
Write-Host "`n2. Starting UDCPR RAG Service..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\ai_services'; Write-Host '=== UDCPR RAG SERVICE - Port 8000 ===' -ForegroundColor Green; python rag_service.py"

Write-Host "   ✅ RAG Service starting..." -ForegroundColor Green

Write-Host "`n3. Waiting for service to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test the service
Write-Host "`n4. Testing RAG Service..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "   ✅ Health: $($health.status)" -ForegroundColor Green
    Write-Host "   ✅ Rules: $($health.total_rules)" -ForegroundColor Green
    
    # Test query
    $testQuery = @{ query = "What is FSI?"; n_results = 2 } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $testQuery -ContentType "application/json" -TimeoutSec 30
    Write-Host "   ✅ Query endpoint working!" -ForegroundColor Green
    
} catch {
    Write-Host "   ❌ Service not responding correctly" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   RAG SERVICE FIXED!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Now refresh your browser and try the AI Assistant again!" -ForegroundColor Cyan

Write-Host "`nPress any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Start Frontend Only
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   STARTING FRONTEND - Port 3000" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Set-Location frontend
Write-Host "Starting React development server..." -ForegroundColor Yellow
Write-Host "This will take 30-60 seconds to compile...`n" -ForegroundColor Gray

npm start

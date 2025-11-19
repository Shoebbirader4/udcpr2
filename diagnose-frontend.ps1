# Diagnose Frontend Issues

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   FRONTEND DIAGNOSTICS" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if frontend directory exists
Write-Host "1. Checking frontend directory..." -ForegroundColor Yellow
if (Test-Path "frontend") {
    Write-Host "   ✅ frontend/ exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ frontend/ not found!" -ForegroundColor Red
    exit
}

# Check package.json
Write-Host "`n2. Checking package.json..." -ForegroundColor Yellow
if (Test-Path "frontend/package.json") {
    Write-Host "   ✅ package.json exists" -ForegroundColor Green
    $pkg = Get-Content "frontend/package.json" | ConvertFrom-Json
    Write-Host "   Name: $($pkg.name)" -ForegroundColor Gray
    Write-Host "   Version: $($pkg.version)" -ForegroundColor Gray
} else {
    Write-Host "   ❌ package.json not found!" -ForegroundColor Red
}

# Check node_modules
Write-Host "`n3. Checking dependencies..." -ForegroundColor Yellow
if (Test-Path "frontend/node_modules") {
    $moduleCount = (Get-ChildItem "frontend/node_modules" -Directory).Count
    Write-Host "   ✅ node_modules exists ($moduleCount packages)" -ForegroundColor Green
} else {
    Write-Host "   ❌ node_modules not found!" -ForegroundColor Red
    Write-Host "   Run: cd frontend && npm install" -ForegroundColor Yellow
}

# Check src directory
Write-Host "`n4. Checking source files..." -ForegroundColor Yellow
if (Test-Path "frontend/src") {
    Write-Host "   ✅ src/ exists" -ForegroundColor Green
    if (Test-Path "frontend/src/App.js") {
        Write-Host "   ✅ App.js exists" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  App.js not found" -ForegroundColor Yellow
    }
    if (Test-Path "frontend/src/index.js") {
        Write-Host "   ✅ index.js exists" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  index.js not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ src/ not found!" -ForegroundColor Red
}

# Check public directory
Write-Host "`n5. Checking public files..." -ForegroundColor Yellow
if (Test-Path "frontend/public") {
    Write-Host "   ✅ public/ exists" -ForegroundColor Green
    if (Test-Path "frontend/public/index.html") {
        Write-Host "   ✅ index.html exists" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  index.html not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ public/ not found!" -ForegroundColor Red
}

# Check port 3000
Write-Host "`n6. Checking port 3000..." -ForegroundColor Yellow
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    $process = Get-Process -Id $port3000.OwningProcess -ErrorAction SilentlyContinue
    Write-Host "   ⚠️  Port 3000 is in use by: $($process.Name) (PID: $($process.Id))" -ForegroundColor Yellow
    Write-Host "   To kill it: taskkill /F /PID $($process.Id)" -ForegroundColor Gray
} else {
    Write-Host "   ✅ Port 3000 is available" -ForegroundColor Green
}

# Try to start (dry run)
Write-Host "`n7. Testing npm start command..." -ForegroundColor Yellow
Set-Location frontend
$npmVersion = npm --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ npm is available (version: $npmVersion)" -ForegroundColor Green
} else {
    Write-Host "   ❌ npm not found!" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   DIAGNOSTICS COMPLETE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "To start frontend, run:" -ForegroundColor Yellow
Write-Host "  .\start-frontend-only.bat" -ForegroundColor Cyan
Write-Host "  OR" -ForegroundColor Gray
Write-Host "  cd frontend" -ForegroundColor Cyan
Write-Host "  npm start" -ForegroundColor Cyan

Write-Host "`nPress any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

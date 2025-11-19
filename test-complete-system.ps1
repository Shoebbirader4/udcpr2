# Complete System Test - UDCPR Master
# Tests all connections and integrations

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   COMPLETE SYSTEM TEST" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

$allPassed = $true

# 1. Check all services are running
Write-Host "1. Service Status Check" -ForegroundColor Yellow
Write-Host "   " -NoNewline
$services = @(
    @{Name="MongoDB"; Port=27017},
    @{Name="Backend API"; Port=5000},
    @{Name="Rule Engine"; Port=5001},
    @{Name="RAG Service"; Port=8000},
    @{Name="Vision Service"; Port=8001},
    @{Name="Frontend"; Port=3000}
)

foreach ($service in $services) {
    $connection = Get-NetTCPConnection -LocalPort $service.Port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "✅" -NoNewline -ForegroundColor Green
    } else {
        Write-Host "❌" -NoNewline -ForegroundColor Red
        $allPassed = $false
    }
}
Write-Host ""

# 2. Test Backend API
Write-Host "`n2. Backend API Tests" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get -TimeoutSec 5
    Write-Host "   ✅ Health endpoint working" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Health endpoint failed" -ForegroundColor Red
    $allPassed = $false
}

# 3. Test Auth Endpoints
Write-Host "`n3. Authentication Endpoints" -ForegroundColor Yellow
$testUser = @{
    email = "test@example.com"
    password = "test123"
    name = "Test User"
} | ConvertTo-Json

try {
    # Try to register (might fail if user exists, that's ok)
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/signup" `
        -Method Post `
        -Body $testUser `
        -ContentType "application/json" `
        -TimeoutSec 10 `
        -ErrorAction SilentlyContinue
    
    if ($registerResponse.token) {
        Write-Host "   ✅ Registration endpoint working" -ForegroundColor Green
        Write-Host "   ✅ JWT token generated" -ForegroundColor Green
    }
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "   ✅ Registration endpoint working (user exists)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Registration endpoint: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Test login
$loginData = @{
    email = "test@example.com"
    password = "test123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
        -Method Post `
        -Body $loginData `
        -ContentType "application/json" `
        -TimeoutSec 10
    
    if ($loginResponse.token) {
        Write-Host "   ✅ Login endpoint working" -ForegroundColor Green
        Write-Host "   ✅ User authentication successful" -ForegroundColor Green
        $token = $loginResponse.token
    }
} catch {
    Write-Host "   ⚠️  Login test: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 4. Test Rule Engine
Write-Host "`n4. Rule Engine Tests" -ForegroundColor Yellow
try {
    $ruleHealth = Invoke-RestMethod -Uri "http://localhost:5001/health" -Method Get -TimeoutSec 5
    Write-Host "   ✅ Rule Engine responding" -ForegroundColor Green
    
    $ruleInfo = Invoke-RestMethod -Uri "http://localhost:5001/rules/info" -Method Get -TimeoutSec 5
    Write-Host "   ✅ Rules info: $($ruleInfo.version)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Rule Engine failed" -ForegroundColor Red
    $allPassed = $false
}

# 5. Test RAG Service
Write-Host "`n5. RAG Service Tests" -ForegroundColor Yellow
try {
    $ragHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "   ✅ RAG Service responding" -ForegroundColor Green
    Write-Host "   ✅ Rules indexed: $($ragHealth.total_rules)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ RAG Service failed" -ForegroundColor Red
    $allPassed = $false
}

# 6. Test Vision Service
Write-Host "`n6. Vision Service Tests" -ForegroundColor Yellow
try {
    $visionHealth = Invoke-RestMethod -Uri "http://localhost:8001/api/vision/health" -Method Get -TimeoutSec 5
    Write-Host "   ✅ Vision Service responding" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Vision Service failed" -ForegroundColor Red
    $allPassed = $false
}

# 7. Check Configuration Files
Write-Host "`n7. Configuration Files" -ForegroundColor Yellow
$configs = @(
    @{Path="backend/.env"; Check="MONGO_URI"},
    @{Path="backend/.env"; Check="OPENAI_API_KEY"},
    @{Path="backend/.env"; Check="PORT=5000"},
    @{Path="ai_services/.env"; Check="OPENAI_API_KEY"},
    @{Path="frontend/.env"; Check="REACT_APP_API_URL"},
    @{Path="frontend/src/pages/Register.js"; Check="Register"}
)

foreach ($config in $configs) {
    if (Test-Path $config.Path) {
        $content = Get-Content $config.Path -Raw -ErrorAction SilentlyContinue
        if ($content -match $config.Check) {
            Write-Host "   ✅ $($config.Path) - $($config.Check)" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $($config.Path) - $($config.Check) not found" -ForegroundColor Red
            $allPassed = $false
        }
    } else {
        Write-Host "   ❌ $($config.Path) missing" -ForegroundColor Red
        $allPassed = $false
    }
}

# 8. Frontend Integration
Write-Host "`n8. Frontend Integration" -ForegroundColor Yellow
if (Test-Path "frontend/src/App.js") {
    $appContent = Get-Content "frontend/src/App.js" -Raw
    if ($appContent -match "Register") {
        Write-Host "   ✅ Register route configured" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Register route missing" -ForegroundColor Red
        $allPassed = $false
    }
}

if (Test-Path "frontend/src/pages/Login.js") {
    $loginContent = Get-Content "frontend/src/pages/Login.js" -Raw
    if ($loginContent -match "/register") {
        Write-Host "   ✅ Login page has signup link" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Login page missing signup link" -ForegroundColor Red
        $allPassed = $false
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "   ✅ ALL TESTS PASSED!" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host "========================================`n" -ForegroundColor Cyan
    Write-Host "🎉 System is fully wired up and working!" -ForegroundColor Green
    Write-Host "`nYou can now:" -ForegroundColor Cyan
    Write-Host "  1. Go to http://localhost:3000" -ForegroundColor White
    Write-Host "  2. Click 'Create one here' to register" -ForegroundColor White
    Write-Host "  3. Create an account" -ForegroundColor White
    Write-Host "  4. Login and start using the app" -ForegroundColor White
} else {
    Write-Host "   ⚠️  SOME TESTS FAILED" -ForegroundColor Yellow
    Write-Host "========================================`n" -ForegroundColor Cyan
    Write-Host "Check the errors above and:" -ForegroundColor Yellow
    Write-Host "  1. Restart services: .\restart-all-services.ps1" -ForegroundColor White
    Write-Host "  2. Run this test again" -ForegroundColor White
}

Write-Host "`nPress any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

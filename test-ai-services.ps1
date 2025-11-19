# Test AI Services
# This script tests if AI features are working

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   AI SERVICES TEST" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Check service status
Write-Host "📋 Checking Service Status...`n" -ForegroundColor Yellow

$services = @(
    @{Name="MongoDB"; Port=27017; Required=$true},
    @{Name="Backend API"; Port=5000; Required=$true},
    @{Name="Rule Engine"; Port=5001; Required=$true},
    @{Name="RAG Service"; Port=8000; Required=$true},
    @{Name="Vision Service"; Port=8001; Required=$false},
    @{Name="Frontend"; Port=3000; Required=$false}
)

$allRunning = $true
foreach ($service in $services) {
    $connection = Get-NetTCPConnection -LocalPort $service.Port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "✅ $($service.Name) - Port $($service.Port)" -ForegroundColor Green
    } else {
        if ($service.Required) {
            Write-Host "❌ $($service.Name) - Port $($service.Port) NOT RUNNING" -ForegroundColor Red
            $allRunning = $false
        } else {
            Write-Host "⚠️  $($service.Name) - Port $($service.Port) NOT RUNNING" -ForegroundColor Yellow
        }
    }
}

if (-not $allRunning) {
    Write-Host "`n⚠️  Required services are not running!" -ForegroundColor Red
    Write-Host "Run: .\restart-all-services.ps1" -ForegroundColor Yellow
    Write-Host "`nPress any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Test RAG Service Health
Write-Host "`n🔍 Testing RAG Service...`n" -ForegroundColor Cyan

try {
    $ragHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✅ RAG Service Health Check" -ForegroundColor Green
    Write-Host "   Status: $($ragHealth.status)" -ForegroundColor Gray
    Write-Host "   Rules Indexed: $($ragHealth.total_rules)" -ForegroundColor Gray
} catch {
    Write-Host "❌ RAG Service health check failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

# Test RAG Service AI Query
Write-Host "`n🤖 Testing AI Query (OpenAI)...`n" -ForegroundColor Cyan

$testQuery = @{
    query = "What is the base FSI for residential buildings in Mumbai?"
    jurisdiction = "Mumbai"
    n_results = 3
} | ConvertTo-Json

try {
    Write-Host "Sending query to RAG service..." -ForegroundColor Gray
    $response = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $testQuery -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "✅ AI Query SUCCESSFUL!" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host "`nQuestion: What is the base FSI for residential buildings in Mumbai?" -ForegroundColor Cyan
    Write-Host "`nAnswer:" -ForegroundColor Yellow
    Write-Host $response.answer -ForegroundColor White
    Write-Host "`nSources: $($response.sources.Count) regulations found" -ForegroundColor Gray
    Write-Host "Confidence: $($response.confidence)" -ForegroundColor Gray
    
    Write-Host "`n✅ OpenAI API is working correctly!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ AI Query FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
    
    if ($_.Exception.Message -match "401" -or $_.Exception.Message -match "Unauthorized") {
        Write-Host "`n⚠️  OpenAI API Key Issue:" -ForegroundColor Yellow
        Write-Host "   - Check if your API key is valid" -ForegroundColor White
        Write-Host "   - Verify it's set in ai_services/.env" -ForegroundColor White
        Write-Host "   - Make sure you have credits in your OpenAI account" -ForegroundColor White
    } elseif ($_.Exception.Message -match "500") {
        Write-Host "`n⚠️  Server Error:" -ForegroundColor Yellow
        Write-Host "   - Check the RAG Service terminal for error details" -ForegroundColor White
        Write-Host "   - OpenAI API key might be invalid or expired" -ForegroundColor White
    }
}

# Test Rule Engine
Write-Host "`n🔧 Testing Rule Engine...`n" -ForegroundColor Cyan

try {
    $ruleHealth = Invoke-RestMethod -Uri "http://localhost:5001/health" -Method Get -TimeoutSec 5
    Write-Host "✅ Rule Engine Health Check" -ForegroundColor Green
    Write-Host "   Status: $($ruleHealth.status)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Rule Engine health check failed" -ForegroundColor Red
}

# Test Backend API
Write-Host "`n🔧 Testing Backend API...`n" -ForegroundColor Cyan

try {
    $backendHealth = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get -TimeoutSec 5
    Write-Host "✅ Backend API Health Check" -ForegroundColor Green
    Write-Host "   Status: $($backendHealth.status)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Backend API health check failed" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   TEST COMPLETE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

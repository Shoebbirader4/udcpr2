# MongoDB Atlas Configuration Helper
# This script helps you configure your MongoDB Atlas connection

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   MONGODB ATLAS CONFIGURATION" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "This script will help you configure MongoDB Atlas for UDCPR Master.`n" -ForegroundColor White

# Get MongoDB Atlas connection string
Write-Host "Step 1: MongoDB Atlas Connection String" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "Get your connection string from MongoDB Atlas:" -ForegroundColor White
Write-Host "  1. Go to https://cloud.mongodb.com/" -ForegroundColor Gray
Write-Host "  2. Click 'Connect' on your cluster" -ForegroundColor Gray
Write-Host "  3. Choose 'Connect your application'" -ForegroundColor Gray
Write-Host "  4. Copy the connection string`n" -ForegroundColor Gray

$mongoUri = Read-Host "Paste your MongoDB Atlas connection string"

# Validate and fix the connection string
if ($mongoUri -notmatch "mongodb\+srv://") {
    Write-Host "`n❌ Invalid connection string. Must start with 'mongodb+srv://'" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Add database name if not present
if ($mongoUri -notmatch "/udcpr_master\?") {
    $mongoUri = $mongoUri -replace "\?", "/udcpr_master?"
    Write-Host "✓ Added database name: udcpr_master" -ForegroundColor Green
}

Write-Host "`n✓ MongoDB connection string configured" -ForegroundColor Green

# Get OpenAI API key (optional)
Write-Host "`nStep 2: OpenAI API Key (Optional)" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "For AI Assistant features, you need an OpenAI API key." -ForegroundColor White
Write-Host "Get one from: https://platform.openai.com/api-keys`n" -ForegroundColor Gray
Write-Host "Press Enter to skip if you don't have one yet." -ForegroundColor Gray

$openaiKey = Read-Host "Paste your OpenAI API key (or press Enter to skip)"

if ([string]::IsNullOrWhiteSpace($openaiKey)) {
    $openaiKey = "your-openai-key-here"
    Write-Host "⚠️  Skipped - AI features will be disabled" -ForegroundColor Yellow
} else {
    Write-Host "✓ OpenAI API key configured" -ForegroundColor Green
}

# Update backend/.env
Write-Host "`nStep 3: Updating Configuration Files" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$backendEnv = @"
# MongoDB Atlas Configuration
MONGO_URI=$mongoUri

# OpenAI API (for LLM parsing and RAG)
OPENAI_API_KEY=$openaiKey

# JWT Secret (change in production)
JWT_SECRET=udcpr-dev-secret-key-change-in-production

# Environment
NODE_ENV=development
PORT=5000
"@

$backendEnv | Out-File -FilePath "backend\.env" -Encoding UTF8
Write-Host "✓ Updated backend/.env" -ForegroundColor Green

# Update ai_services/.env
$aiEnv = @"
# OpenAI API Configuration
OPENAI_API_KEY=$openaiKey

# MongoDB Atlas Configuration (for vector store)
MONGO_URI=$mongoUri

# Environment
ENVIRONMENT=development
"@

$aiEnv | Out-File -FilePath "ai_services\.env" -Encoding UTF8
Write-Host "✓ Updated ai_services/.env" -ForegroundColor Green

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   CONFIGURATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "✅ MongoDB Atlas configured" -ForegroundColor Green
if ($openaiKey -ne "your-openai-key-here") {
    Write-Host "✅ OpenAI API key configured" -ForegroundColor Green
} else {
    Write-Host "⚠️  OpenAI API key not configured (AI features disabled)" -ForegroundColor Yellow
}

Write-Host "`n📋 IMPORTANT: Whitelist Your IP in MongoDB Atlas" -ForegroundColor Yellow
Write-Host "  1. Go to MongoDB Atlas → Network Access" -ForegroundColor White
Write-Host "  2. Click 'Add IP Address'" -ForegroundColor White
Write-Host "  3. Add your current IP or 'Allow from Anywhere' (0.0.0.0/0)`n" -ForegroundColor White

Write-Host "🚀 Ready to Start!" -ForegroundColor Cyan
Write-Host "Run: " -NoNewline -ForegroundColor White
Write-Host ".\start-services-fixed.ps1" -ForegroundColor Green

Write-Host "`nPress any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

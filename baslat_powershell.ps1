# AI Sistem Başlatma Script'i - PowerShell

Write-Host "🚀 AI Sistem Baslatiliyor..." -ForegroundColor Green
Write-Host ""

# Backend başlat
Write-Host "📦 Backend baslatiliyor..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/k", "python backend/app.py" -WindowStyle Normal

Write-Host "⏳ 5 saniye bekleniyor..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Frontend başlat (PowerShell için ayrı komutlar)
Write-Host "🌐 Frontend baslatiliyor..." -ForegroundColor Cyan
$frontendCmd = @"
cd frontend
npm start
"@

Start-Process -FilePath "cmd" -ArgumentList "/k", $frontendCmd -WindowStyle Normal

Write-Host ""
Write-Host "✅ Sistem baslatildi!" -ForegroundColor Green
Write-Host "📊 Frontend: http://localhost:3000" -ForegroundColor Blue
Write-Host "🔧 Backend: http://localhost:5000" -ForegroundColor Blue
Write-Host ""
Write-Host "🎯 Test: http://localhost:3000" -ForegroundColor Magenta
Write-Host ""

Read-Host "Devam etmek icin Enter'a basin" 
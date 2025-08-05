# AI Satıcı Risk Analiz Sistemi - PowerShell Başlatma Script'i

Write-Host "🚀 AI Satici Risk Analiz Sistemi Baslatiliyor..." -ForegroundColor Green
Write-Host ""

# Sanal ortamı etkinleştir
Write-Host "🔧 Sanal ortam etkinlestiriliyor..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
Write-Host "✅ Sanal ortam hazir" -ForegroundColor Green
Write-Host ""

# Mevcut süreçleri kontrol et
Write-Host "🔍 Mevcut backend sureclerini kontrol ediliyor..." -ForegroundColor Yellow
$backendRunning = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue

if ($backendRunning) {
    Write-Host "⚠️ Backend zaten calisiyor (Port 5000)" -ForegroundColor Yellow
} else {
    Write-Host "📦 1. Backend baslatiliyor..." -ForegroundColor Cyan
    Start-Process -FilePath "cmd" -ArgumentList "/k", "call .venv\Scripts\activate && python backend/app.py" -WindowStyle Normal
    Write-Host "⏳ Backend'in baslamasini bekliyoruz..." -ForegroundColor Yellow
    Start-Sleep -Seconds 8
}

Write-Host ""
$frontendRunning = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

if ($frontendRunning) {
    Write-Host "⚠️ Frontend zaten calisiyor (Port 3000)" -ForegroundColor Yellow
} else {
    Write-Host "🌐 2. Frontend baslatiliyor..." -ForegroundColor Cyan
    Start-Process -FilePath "cmd" -ArgumentList "/k", "call .venv\Scripts\activate && cd frontend && npm start" -WindowStyle Normal
    Write-Host "⏳ Frontend'in baslamasini bekliyoruz..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

Write-Host ""
Write-Host "✅ Sistem baslatildi!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Frontend: http://localhost:3000" -ForegroundColor Blue
Write-Host "🔧 Backend: http://localhost:5000" -ForegroundColor Blue
Write-Host "🗄️ Database: localhost:5434" -ForegroundColor Blue
Write-Host ""
Write-Host "🎯 KULLANIM:" -ForegroundColor Magenta
Write-Host "1. Frontend'e gidin: http://localhost:3000" -ForegroundColor White
Write-Host "2. Urun arayın (ornek: 'samsung telefon')" -ForegroundColor White
Write-Host "3. 'Detaylari Gor' butonuna basin" -ForegroundColor White
Write-Host "4. 'Risk Analizi' butonuna basin" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Sistemi kapatmak icin acilan terminal pencerelerini kapatin" -ForegroundColor Red
Write-Host ""

Read-Host "Devam etmek icin Enter'a basin" 
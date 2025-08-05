@echo off

echo 🚀 AI Satici Risk Analiz Sistemi Baslatiliyor...
echo.

REM Sanal ortamı etkinleştir
echo 🔧 Sanal ortam etkinlestiriliyor...
call .venv\Scripts\activate
echo ✅ Sanal ortam hazir
echo.

REM Mevcut süreçleri kontrol et (PowerShell kullanarak)
echo 🔍 Mevcut backend sureclerini kontrol ediliyor...
powershell -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue" > nul 2>&1
if %errorlevel% == 0 (
    echo ⚠️ Backend zaten calisiyor (Port 5000)
) else (
    echo 📦 1. Backend baslatiliyor...
    start "AI Backend Server" cmd /k "call .venv\Scripts\activate && python backend/app.py"
    echo ⏳ Backend'in baslamasini bekliyoruz...
    timeout /t 8 /nobreak > nul
)

echo.
powershell -Command "Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue" > nul 2>&1
if %errorlevel% == 0 (
    echo ⚠️ Frontend zaten calisiyor (Port 3000)
) else (
    echo 🌐 2. Frontend baslatiliyor...
    start "AI Frontend Server" cmd /k "call .venv\Scripts\activate && cd frontend && npm start"
    echo ⏳ Frontend'in baslamasini bekliyoruz...
    timeout /t 10 /nobreak > nul
)

echo.
echo ✅ Sistem baslatildi!
echo.
echo 📊 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:5000
echo 🗄️ Database: localhost:5434
echo.
echo 🎯 KULLANIM:
echo 1. Frontend'e gidin: http://localhost:3000
echo 2. Urun arayın (ornek: "samsung telefon")
echo 3. "Detaylari Gor" butonuna basin
echo 4. "Risk Analizi" butonuna basin
echo.
echo 🛑 Sistemi kapatmak icin acilan terminal pencerelerini kapatin
echo.

pause
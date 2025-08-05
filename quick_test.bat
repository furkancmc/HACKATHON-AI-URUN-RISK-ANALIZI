@echo off
chcp 65001 > nul

echo 🧪 AI Sistem Hızlı Test
echo.

REM Backend testi
echo 🔍 Backend durumu kontrol ediliyor...
curl -s http://localhost:5000/api/health > nul
if %errorlevel% == 0 (
    echo ✅ Backend çalışıyor (Port 5000)
) else (
    echo ❌ Backend çalışmıyor (Port 5000)
    echo 🚀 Backend başlatmak için: start_system.bat
    pause
    exit
)

REM Frontend testi
echo 🔍 Frontend durumu kontrol ediliyor...
curl -s http://localhost:3000 > nul
if %errorlevel% == 0 (
    echo ✅ Frontend çalışıyor (Port 3000)
) else (
    echo ❌ Frontend çalışmıyor (Port 3000)
    echo 🚀 Frontend başlatmak için: start_system.bat
)

echo.
echo 📊 Sistem Durumu:
echo ✅ Backend: http://localhost:5000/api/health
echo ✅ Frontend: http://localhost:3000
echo 🗄️ Database: localhost:5434
echo.
echo 🎯 Test etmek için:
echo 1. http://localhost:3000 adresine gidin
echo 2. "samsung telefon" arayın
echo 3. "Detayları Gör" butonuna basın
echo 4. "Risk Analizi" butonuna basın
echo.

pause
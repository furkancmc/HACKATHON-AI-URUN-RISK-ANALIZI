@echo off
echo 🧪 AI Sistem Test Ediliyor...
echo.

echo 🔍 Backend testi...
curl -s http://localhost:5000/api/health > nul
if %errorlevel% == 0 (
    echo ✅ Backend çalışıyor
) else (
    echo ❌ Backend çalışmıyor
    echo 🚀 Backend başlatmak için: python backend/app.py
    pause
    exit
)

echo.
echo 🔍 Frontend testi...
curl -s http://localhost:3000 > nul
if %errorlevel% == 0 (
    echo ✅ Frontend çalışıyor
) else (
    echo ❌ Frontend çalışmıyor
    echo 🚀 Frontend başlatmak için: cd frontend && npm start
    pause
    exit
)

echo.
echo 🎉 SİSTEM HAZIR!
echo 📊 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:5000
echo.
echo 🎯 Test için:
echo 1. http://localhost:3000 adresine gidin
echo 2. "samsung telefon" arayın
echo 3. "Detayları Gör" butonuna basın
echo 4. "Risk Analizi" butonuna basın
echo.
pause 
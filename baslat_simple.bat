@echo off
echo 🚀 AI Sistem Baslatiliyor...
echo.

echo 📦 Backend baslatiliyor...
start "Backend" cmd /k "python backend/app.py"

echo.
echo 🌐 Frontend baslatiliyor...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo ✅ Sistem baslatildi!
echo 📊 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:5000
echo.
echo 🎯 Test: http://localhost:3000
echo.
pause 
#!/bin/bash

echo "🚀 AI Satıcı Risk Analiz Sistemi Başlatılıyor..."
echo

# Sanal ortamı etkinleştir
echo "🔧 Sanal ortam etkinleştiriliyor..."
source .venv/bin/activate
echo "✅ Sanal ortam hazır"
echo

# Mevcut süreçleri kontrol et
echo "🔍 Mevcut backend süreçlerini kontrol ediliyor..."
if lsof -i :5000 >/dev/null 2>&1; then
    echo "⚠️ Backend zaten çalışıyor (Port 5000)"
    BACKEND_PID=""
else
    echo "📦 1. Backend başlatılıyor..."
    (python backend/app.py) &
    BACKEND_PID=$!
    echo "⏳ Backend'in başlamasını bekliyoruz..."
    sleep 8
fi

echo
if lsof -i :3000 >/dev/null 2>&1; then
    echo "⚠️ Frontend zaten çalışıyor (Port 3000)"
    FRONTEND_PID=""
else
    echo "🌐 2. Frontend başlatılıyor..."
    (cd frontend && npm start) &
    FRONTEND_PID=$!
    echo "⏳ Frontend'in başlamasını bekliyoruz..."
    sleep 10
fi

echo
echo "✅ Sistem başlatıldı!"
echo
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:5000"
echo "🗄️ Database: localhost:5434"
echo
echo "🎯 KULLANIM:"
echo "1. Frontend'e gidin: http://localhost:3000"
echo "2. Ürün arayın (örnek: \"samsung telefon\")"
echo "3. \"Detayları Gör\" butonuna basın"
echo "4. \"Risk Analizi\" butonuna basın"
echo
echo "🛑 Sistemi kapatmak için Ctrl+C'ye basın"
echo

# Ctrl+C ile kapatma
if [ -n "$BACKEND_PID" ] || [ -n "$FRONTEND_PID" ]; then
    trap "echo 'Sistem kapatılıyor...'; [ -n '$BACKEND_PID' ] && kill $BACKEND_PID; [ -n '$FRONTEND_PID' ] && kill $FRONTEND_PID; exit" INT TERM
    
    echo "Sistem çalışıyor..."
    [ -n "$BACKEND_PID" ] && wait $BACKEND_PID
    [ -n "$FRONTEND_PID" ] && wait $FRONTEND_PID
else
    echo "Her iki servis de zaten çalışıyor. Terminal'i kapatabilirsiniz."
    read -p "Devam etmek için Enter'a basın..."
fi
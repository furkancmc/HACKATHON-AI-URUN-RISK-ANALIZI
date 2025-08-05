# 🚀 AI Satıcı Risk Analiz Sistemi - Kullanım Talimatları

## ⚡ **HIZLI BAŞLATMA**

### **Windows:**
```bash
# Çift tıklayın:
start_system.bat
```

### **Linux/Mac:**
```bash
chmod +x start_system.sh
./start_system.sh
```

## 🔧 **MANUEL BAŞLATMA**

### **1. Sanal Ortamı Etkinleştirin**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac  
source .venv/bin/activate
```

### **2. Backend Başlatın**
```bash
python backend/app.py
```

### **3. Frontend Başlatın** (Yeni terminal)
```bash
cd frontend
npm start
```

## 🌐 **ERİŞİM URL'LERİ**

- **🖥️ Ana Uygulama:** http://localhost:3000
- **🔧 Backend API:** http://localhost:5000
- **🗄️ PostgreSQL:** localhost:5434

## 🎯 **NASIL KULLANILIR**

### **1. Ürün Arama**
- Ana sayfaya gidin: http://localhost:3000
- Arama kutusuna ürün yazın (örn: "samsung telefon")
- "🔍 Ürün Ara" butonuna basın

### **2. Ürün Detaylarını Görüntüleme**
- Arama sonuçlarında "👁️ Detayları Gör" butonuna basın
- Modern, kategorize edilmiş ürün bilgilerini görün:
  - ⚠️ **Risk Analizi:** Renkli skorlar ve eylem planı
  - 📦 **Temel Bilgiler:** Ürün adı, marka, model
  - 💰 **Fiyatlandırma:** Fiyat, rating, indirim
  - 📊 **Stok Durumu:** Stok, tedarik, satıcı bilgileri
  - 🔧 **Teknik Özellikler:** Özellikler, garanti
  - 📝 **Açıklama:** Detaylı ürün açıklaması

### **3. AI Risk Analizi**
- Arama sonuçlarında "🤖 Risk Analizi" butonuna basın
- Gemini AI'nin satıcı odaklı analizi görün:
  - Risk değerlendirmesi
  - Karlılık analizi
  - Pazar önerileri
  - Eylem planı

### **4. Diğer Özellikler**
- **📊 Dashboard:** Tablo istatistikleri
- **💬 AI Asistan:** Genel sohbet özelliği
- **⚙️ Sistem Yönetimi:** Embedding oluşturma

## 🛠️ **SORUN GİDERME**

### **Backend Çalışmıyor mu?**
```bash
# Durumu kontrol edin
curl http://localhost:5000/api/health

# Yeniden başlatın
python backend/app.py
```

### **Frontend Çalışmıyor mu?**
```bash
# Frontend dizinine gidin
cd frontend

# Bağımlılıkları yükleyin
npm install

# Başlatın
npm start
```

### **ESLint Uyarıları**
- Kullanılmayan import'lar otomatik temizlenir
- Mevcut uyarılar sistem işlevselliğini etkilemez

### **Port Çakışması**
- Backend: Port 5000 (değiştirmek için backend/app.py)
- Frontend: Port 3000 (değiştirmek için package.json)
- Database: Port 5434

## 🧪 **HIZLI TEST**

### **Windows:**
```bash
quick_test.bat
```

### **Manuel Test:**
```bash
# Backend testi
curl http://localhost:5000/api/health

# Frontend testi
curl http://localhost:3000
```

## 📋 **ÖZELLİKLER**

### ✅ **Çalışan Özellikler:**
- 🔍 Ürün arama (AI destekli)
- 👁️ Detaylı ürün görüntüleme (modern UI)
- 🤖 AI risk analizi (Gemini AI)
- 📊 Dashboard ve istatistikler
- 💬 AI asistan sohbeti
- 📱 Responsive tasarım (mobil uyumlu)

### 🎨 **Modern UI Özellikleri:**
- Tematik bilgi blokları
- Renkli risk skorları
- Hover efektleri
- Türkçe arayüz
- Kategorize edilmiş veriler

## 🆘 **YARDIM**

### **Sistem durumunu kontrol etmek için:**
- Windows: `quick_test.bat`
- Backend: http://localhost:5000/api/health
- Frontend: http://localhost:3000

### **Yaygın Sorunlar:**
1. **"Backend çalışmıyor"** → `python backend/app.py`
2. **"npm start hatası"** → `cd frontend && npm install`
3. **"Port kullanımda"** → Mevcut süreçleri kapatın
4. **"Database bağlantı hatası"** → PostgreSQL'in çalıştığından emin olun

**🎉 Sistem hazır! Başarılı testler dileriz!**
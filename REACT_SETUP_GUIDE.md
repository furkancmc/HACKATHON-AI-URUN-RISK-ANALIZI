# 🚀 React AI Satıcı Risk Analiz Sistemi - Kurulum Rehberi

## 📁 Yeni Dosya Yapısı

```
hackathon-scraping/
├── frontend/                    # React Frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/          # React bileşenleri
│   │   ├── pages/              # Ana sayfalar
│   │   │   ├── ProductSearch.js    # Ürün arama sayfası
│   │   │   ├── Dashboard.js        # Dashboard sayfası  
│   │   │   ├── AIAssistant.js      # AI asistan sayfası
│   │   │   └── SystemManagement.js # Sistem yönetimi
│   │   ├── services/
│   │   │   └── api.js          # API servisleri
│   │   ├── App.js              # Ana React uygulaması
│   │   ├── index.js            # React entry point
│   │   └── index.css           # CSS stilleri
│   └── package.json            # React bağımlılıkları
├── backend/                     # Python Flask Backend
│   ├── app.py                  # Flask API sunucusu
│   └── requirements.txt        # Python bağımlılıkları
├── run_embedding_creation.py    # Telefon/kulaklık tabloları aktarım scripti
├── start_system.bat            # Windows başlatma scripti
├── start_system.sh             # Linux/Mac başlatma scripti
└── REACT_SETUP_GUIDE.md       # Bu dosya
```

## 🛠️ Kurulum Adımları

### 1. Backend Kurulumu

```bash
# Backend klasörüne git
cd backend

# Python bağımlılıklarını yükle
pip install -r requirements.txt
```

### 2. Frontend Kurulumu

```bash
# Frontend klasörüne git  
cd frontend

# Node.js bağımlılıklarını yükle
npm install
```

### 3. Telefon ve Kulaklık Tablolarını Aktar

```bash
# Ana dizinde
python run_embedding_creation.py
```

## 🚀 Sistemi Başlatma

### Windows:
```bash
start_system.bat
```

### Linux/Mac:
```bash
chmod +x start_system.sh
./start_system.sh
```

### Manuel Başlatma:

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## 🌐 Erişim URL'leri

- **Frontend (React):** http://localhost:3000
- **Backend (Flask):** http://localhost:5000
- **API Health Check:** http://localhost:5000/api/health

## ✅ Düzeltilen Problemler

### 1. 🔧 Detayları Gör Butonu
- **Önceki Problem:** Session state yönetimi hatalıydı
- **React Çözümü:** Modal ile düzgün state yönetimi
- **Özellikler:** 
  - Risk analizi bilgileri öne çıkarılır
  - Tüm ürün verileri JSON formatında gösterilir
  - Kapat butonu ile modal kapatılır

### 2. 🤖 AI Risk Analizi Butonu  
- **Önceki Problem:** AI analizi çalışmıyordu
- **React Çözümü:** Ayrı modal ve API endpoint
- **Özellikler:**
  - Satıcı odaklı risk analizi
  - Tüm risk skorları gösterilir
  - Loading state ile kullanıcı deneyimi

### 3. 📊 Tablo Sayısı Sorunu
- **Önceki Problem:** Yanlış tablo sayısı gösteriliyordu  
- **React Çözümü:** API'den gerçek zamanlı veri
- **Özellikler:**
  - Sadece aktif tablolar sayılır
  - Gerçek zamanlı güncelleme
  - Dashboard'da doğru metrikler

### 4. 📱 Telefon ve Kulaklık Tabloları
- **Önceki Problem:** JSON veriler aktarılmamıştı
- **React Çözümü:** Otomatik aktarım scripti
- **Özellikler:**
  - `run_embedding_creation.py` ile otomatik aktarım
  - Embedding'ler otomatik oluşturulur
  - Sistem yönetiminden kontrol edilebilir

## 🎯 React'in Avantajları

### 1. **Modern UI/UX**
- Ant Design ile profesyonel arayüz
- Responsive tasarım
- Smooth animasyonlar ve geçişler

### 2. **Gerçek Zamanlı Güncellemeler**
- API'den canlı veri
- Otomatik state yönetimi
- Loading states

### 3. **Modüler Yapı**
- Sayfa bazında bileşenler
- Yeniden kullanılabilir kod
- Kolay bakım

### 4. **Performans**
- Client-side rendering
- Hızlı sayfa geçişleri
- Optimized bundle

## 🔧 API Endpoints

### Sistem
- `GET /api/health` - Sistem durumu
- `GET /api/test` - Servis testleri

### Veri
- `GET /api/tables/stats` - Tablo istatistikleri
- `POST /api/search` - Ürün arama
- `GET /api/product/{id}/details` - Ürün detayları

### AI
- `POST /api/ai/analyze` - Ürün risk analizi
- `POST /api/ai/chat` - AI sohbet

### Yönetim
- `POST /api/embeddings/create` - Embedding oluştur

## 🎨 Özellikler

### 🔍 Ürün Risk Arama
- Doğal dil ile arama
- Gelişmiş filtreler (fiyat, rating, marka)
- Risk skorları ile sonuçlar
- Modal'larla detay görüntüleme

### 📊 Satış Dashboard  
- Gerçek zamanlı metrikler
- Interaktif grafikler (Recharts)
- Tablo bazında analiz
- Embedding kapsama oranları

### 🤖 AI Satış Danışmanı
- Satıcı odaklı sohbet
- Context-aware yanıtlar
- Örnek sorular
- Chat geçmişi

### ⚙️ Sistem Yönetimi
- Servis durumu kontrolü
- Sistem testleri
- Embedding oluşturma
- Performans metrikleri

## 🚨 Sorun Giderme

### Backend Bağlantı Sorunu
```bash
# Backend'in çalıştığını kontrol et
curl http://localhost:5000/api/health
```

### Frontend Build Sorunu
```bash
cd frontend
npm install
npm start
```

### Embedding Sorunu
```bash
python run_embedding_creation.py
```

### Veritabanı Sorunu
- PostgreSQL'in 5434 portunda çalıştığını kontrol et
- pgvector extension'ının yüklü olduğunu kontrol et

## 🎉 Sistem Artık Hazır!

React tabanlı modern web uygulaması ile:
- ✅ Çalışan detay butonları
- ✅ Fonksiyonel AI analizi  
- ✅ Doğru tablo sayısı
- ✅ Telefon ve kulaklık verileri
- ✅ Satıcı odaklı risk analizi
- ✅ Modern ve hızlı arayüz

**Kullanmaya başlayın:** http://localhost:3000
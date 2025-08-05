# Hackathon Scraping Projesi

Bu proje, web scraping ve AI destekli ürün analizi sistemi içerir. Backend Python Flask API'si ve React frontend'i ile geliştirilmiştir.

## 🚀 Özellikler

- Web scraping ile ürün verisi toplama
- AI destekli ürün analizi ve öneriler
- Vektör veritabanı ile semantik arama
- Modern React frontend
- Docker desteği
- PostgreSQL + pgvector entegrasyonu

## 📋 Gereksinimler

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Docker (opsiyonel)

## 🛠️ Kurulum

### 1. Repository'yi klonlayın
```bash
git clone https://github.com/kullaniciadi/hackathon-scraping.git
cd hackathon-scraping
```

### 2. Backend kurulumu
```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend kurulumu
```bash
cd frontend
npm install
```

### 4. Veritabanı kurulumu
```bash
# PostgreSQL kurulumu ve pgvector eklentisi
# setup_pgvector.sql dosyasını çalıştırın
```

### 5. Environment değişkenleri
```bash
# .env dosyasını oluşturun
cp env.example .env
# Gerekli değişkenleri düzenleyin
```

## 🚀 Çalıştırma

### Geliştirme modu
```bash
# Backend
cd backend
python app.py

# Frontend (yeni terminal)
cd frontend
npm start
```

### Docker ile
```bash
docker-compose up -d
```

## 📁 Proje Yapısı

```
hackathon-scraping/
├── backend/                 # Flask API
│   ├── app.py              # Ana uygulama
│   └── requirements.txt    # Python bağımlılıkları
├── frontend/               # React uygulaması
│   ├── src/
│   │   ├── components/     # React bileşenleri
│   │   ├── pages/         # Sayfa bileşenleri
│   │   └── services/      # API servisleri
│   └── package.json
├── tests/                  # Test dosyaları
├── docker-compose.yml      # Docker konfigürasyonu
└── README.md
```

## 🔧 API Endpoints

- `GET /api/products` - Ürün listesi
- `POST /api/search` - Semantik arama
- `GET /api/ai-assistant` - AI asistan
- `POST /api/scrape` - Web scraping

## 🧪 Test

```bash
# Backend testleri
python -m pytest tests/

# Frontend testleri
cd frontend
npm test
```

## 📝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🤝 İletişim

- Proje Linki: [https://github.com/kullaniciadi/hackathon-scraping](https://github.com/kullaniciadi/hackathon-scraping)

## 🙏 Teşekkürler

Bu proje hackathon sürecinde geliştirilmiştir. 
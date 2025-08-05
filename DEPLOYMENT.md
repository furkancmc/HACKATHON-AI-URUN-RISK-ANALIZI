# 🚀 Deployment Rehberi

Bu rehber, AI Destekli Satıcı Risk Analiz Sistemi'ni farklı ortamlara deploy etmek için kullanılır.

## 📋 Ön Gereksinimler

### Sistem Gereksinimleri
- **CPU**: 4+ çekirdek
- **RAM**: 16GB minimum
- **Disk**: 50GB+ SSD
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+

### Yazılım Gereksinimleri
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Python**: 3.9+
- **Node.js**: 16+
- **PostgreSQL**: 13+

## 🐳 Docker ile Deployment

### 1. Hızlı Başlatma
```bash
# Projeyi klonlayın
git clone https://github.com/kullanici/hackathon-scraping.git
cd hackathon-scraping

# Ortam değişkenlerini ayarlayın
cp .env.example .env
# .env dosyasını düzenleyin

# Docker Compose ile başlatın
docker-compose up -d
```

### 2. Ortam Değişkenleri
`.env` dosyası oluşturun:
```env
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/ai_seller_analysis

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Flask
FLASK_ENV=production
FLASK_DEBUG=False

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your_secret_key_here
```

### 3. Production Ayarları
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d

# Logları kontrol edin
docker-compose logs -f

# Servisleri durdurun
docker-compose down
```

## ☁️ Cloud Deployment

### AWS EC2 Deployment

#### 1. EC2 Instance Oluşturma
```bash
# Ubuntu 20.04 LTS instance başlatın
# t3.large veya üzeri önerilir
# Security Group: 22, 80, 443, 3000, 5000 portları açın
```

#### 2. Instance'a Bağlanma
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 3. Sistem Kurulumu
```bash
# Sistem güncellemeleri
sudo apt update && sudo apt upgrade -y

# Docker kurulumu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose kurulumu
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Git kurulumu
sudo apt install git -y
```

#### 4. Uygulama Deployment
```bash
# Projeyi klonlayın
git clone https://github.com/kullanici/hackathon-scraping.git
cd hackathon-scraping

# Ortam değişkenlerini ayarlayın
cp .env.example .env
nano .env

# Uygulamayı başlatın
docker-compose up -d

# Nginx reverse proxy kurulumu
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/ai-seller
```

#### 5. Nginx Konfigürasyonu
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Nginx'i etkinleştirin
sudo ln -s /etc/nginx/sites-available/ai-seller /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Google Cloud Platform (GCP)

#### 1. Compute Engine Instance
```bash
# Instance oluşturun
gcloud compute instances create ai-seller-instance \
    --zone=us-central1-a \
    --machine-type=e2-standard-4 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server,https-server

# Firewall kuralları
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --target-tags=http-server \
    --description="Allow HTTP traffic"

gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --target-tags=https-server \
    --description="Allow HTTPS traffic"
```

#### 2. Deployment Script
```bash
#!/bin/bash
# deploy.sh

# Sistem güncellemeleri
sudo apt update && sudo apt upgrade -y

# Docker kurulumu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose kurulumu
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Projeyi klonlayın
git clone https://github.com/kullanici/hackathon-scraping.git
cd hackathon-scraping

# Ortam değişkenlerini ayarlayın
cp .env.example .env
# .env dosyasını düzenleyin

# Uygulamayı başlatın
docker-compose up -d
```

### Azure

#### 1. Azure VM Oluşturma
```bash
# Resource Group oluşturun
az group create --name ai-seller-rg --location eastus

# VM oluşturun
az vm create \
    --resource-group ai-seller-rg \
    --name ai-seller-vm \
    --image UbuntuLTS \
    --size Standard_D4s_v3 \
    --admin-username azureuser \
    --generate-ssh-keys

# Network Security Group kuralları
az network nsg rule create \
    --resource-group ai-seller-rg \
    --nsg-name ai-seller-vmNSG \
    --name allow-http \
    --protocol tcp \
    --priority 1000 \
    --destination-port-range 80

az network nsg rule create \
    --resource-group ai-seller-rg \
    --nsg-name ai-seller-vmNSG \
    --name allow-https \
    --protocol tcp \
    --priority 1001 \
    --destination-port-range 443
```

## 🔒 SSL/HTTPS Kurulumu

### Let's Encrypt ile SSL
```bash
# Certbot kurulumu
sudo apt install certbot python3-certbot-nginx -y

# SSL sertifikası alın
sudo certbot --nginx -d your-domain.com

# Otomatik yenileme
sudo crontab -e
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring ve Logging

### Prometheus + Grafana
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Log Aggregation
```bash
# ELK Stack kurulumu
docker-compose -f docker-compose.logging.yml up -d
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.KEY }}
          script: |
            cd /opt/ai-seller
            git pull origin main
            docker-compose down
            docker-compose up -d --build
```

## 🐛 Sorun Giderme

### Yaygın Sorunlar

#### Port Çakışması
```bash
# Port kullanımını kontrol edin
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :3000

# Servisleri durdurun
sudo systemctl stop nginx
docker-compose down
```

#### Disk Alanı
```bash
# Disk kullanımını kontrol edin
df -h

# Docker temizliği
docker system prune -a
docker volume prune
```

#### Memory Sorunları
```bash
# Memory kullanımını kontrol edin
free -h

# Docker memory limitleri
docker-compose.yml'de memory limitleri ekleyin
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- PostgreSQL ayarları
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Vektör indeksleri
CREATE INDEX CONCURRENTLY idx_product_embeddings 
ON products USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

### Caching
```python
# Redis cache implementasyonu
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            result = redis_client.get(cache_key)
            if result:
                return json.loads(result)
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## 🔐 Security Best Practices

### Environment Variables
```bash
# Hassas bilgileri environment variables olarak saklayın
export DATABASE_URL="postgresql://user:pass@host:port/db"
export GEMINI_API_KEY="your_api_key"
export SECRET_KEY="your_secret_key"
```

### Firewall Configuration
```bash
# UFW firewall kurulumu
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 3000  # Frontend port'unu dışarıya açmayın
sudo ufw deny 5000  # Backend port'unu dışarıya açmayın
```

### Regular Updates
```bash
# Otomatik güncelleme scripti
#!/bin/bash
# update.sh

# Sistem güncellemeleri
sudo apt update && sudo apt upgrade -y

# Docker image güncellemeleri
docker-compose pull
docker-compose up -d --build

# Log rotasyonu
sudo logrotate /etc/logrotate.conf
```

---

Bu rehber ile sisteminizi güvenli ve performanslı bir şekilde deploy edebilirsiniz. 
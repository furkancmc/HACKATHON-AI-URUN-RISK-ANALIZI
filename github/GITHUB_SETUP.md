# GitHub'a Yükleme Rehberi

Bu dosya, projenizi GitHub'a yükleme adımlarını detaylı olarak açıklar.

## 📋 Ön Gereksinimler

1. **Git kurulu olmalı** - [Git İndirme](https://git-scm.com/downloads)
2. **GitHub hesabı** - [GitHub Kayıt](https://github.com/signup)
3. **GitHub CLI (opsiyonel)** - [GitHub CLI İndirme](https://cli.github.com/)

## 🚀 Adım Adım GitHub'a Yükleme

### 1. GitHub'da Repository Oluşturma

1. GitHub.com'a giriş yapın
2. Sağ üst köşedeki "+" butonuna tıklayın
3. "New repository" seçin
4. Repository adını girin: `hackathon-scraping`
5. Açıklama ekleyin: "Web scraping ve AI destekli ürün analizi sistemi"
6. **Public** veya **Private** seçin
7. **"Add a README file"** işaretlemeyin (bizim README'miz var)
8. **"Add .gitignore"** işaretlemeyin (bizim .gitignore'umuz var)
9. **"Choose a license"** seçin: MIT License
10. "Create repository" butonuna tıklayın

### 2. Yerel Git Repository'si Başlatma

```bash
# Proje klasörüne gidin
cd C:\Users\Furkan\Desktop\HACKATHON\hackathon-scraping

# Git repository'si başlatın
git init

# GitHub repository'sini remote olarak ekleyin
git remote add origin https://github.com/KULLANICI_ADINIZ/hackathon-scraping.git
```

### 3. Dosyaları Hazırlama

```bash
# Tüm dosyaları staging area'ya ekleyin
git add .

# İlk commit'i yapın
git commit -m "Initial commit: Hackathon scraping project"

# Main branch'i oluşturun (eğer yoksa)
git branch -M main
```

### 4. GitHub'a Push Etme

```bash
# Dosyaları GitHub'a yükleyin
git push -u origin main
```

## 🔧 Önemli Dosyalar

### .gitignore
- Gereksiz dosyaları GitHub'a yüklememek için
- `github/.gitignore` dosyasını proje ana dizinine kopyalayın

### README.md
- Proje açıklaması ve kurulum talimatları
- `github/README.md` dosyasını proje ana dizinine kopyalayın

### LICENSE
- MIT lisansı dosyası (GitHub'da otomatik oluşturulabilir)

## 📁 Yüklenecek Dosyalar

### ✅ Yüklenecek Dosyalar
- `backend/` - Flask API
- `frontend/` - React uygulaması
- `tests/` - Test dosyaları
- `docker-compose.yml` - Docker konfigürasyonu
- `Dockerfile` - Docker image
- `requirements.txt` - Python bağımlılıkları
- `package.json` - Node.js bağımlılıkları
- `README.md` - Proje açıklaması
- `LICENSE` - Lisans dosyası
- `.gitignore` - Git ignore kuralları

### ❌ Yüklenmeyecek Dosyalar
- `__pycache__/` klasörleri
- `node_modules/` klasörü
- `.env` dosyaları
- Log dosyaları
- Geçici dosyalar
- IDE ayar dosyaları

## 🛠️ Ek Ayarlar

### GitHub Pages (Opsiyonel)
1. Repository Settings > Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: / (root)
5. Save

### GitHub Actions (Opsiyonel)
CI/CD pipeline için `.github/workflows/` klasörü oluşturabilirsiniz.

## 🔍 Kontrol Listesi

- [ ] GitHub repository oluşturuldu
- [ ] Git init yapıldı
- [ ] Remote origin eklendi
- [ ] .gitignore dosyası hazırlandı
- [ ] README.md dosyası hazırlandı
- [ ] İlk commit yapıldı
- [ ] GitHub'a push edildi
- [ ] Repository public/private ayarı yapıldı
- [ ] Lisans dosyası eklendi

## 🚨 Hata Çözümleri

### Authentication Hatası
```bash
# Personal Access Token kullanın
git remote set-url origin https://TOKEN@github.com/KULLANICI_ADINIZ/hackathon-scraping.git
```

### Large File Hatası
```bash
# Büyük dosyaları .gitignore'a ekleyin
# veya Git LFS kullanın
```

### Branch Hatası
```bash
# Branch adını değiştirin
git branch -M main
```

## 📞 Yardım

Eğer sorun yaşarsanız:
1. GitHub Docs: https://docs.github.com/
2. Git Docs: https://git-scm.com/doc
3. Stack Overflow: https://stackoverflow.com/ 
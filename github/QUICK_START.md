# 🚀 Hızlı Başlangıç Rehberi

Bu rehber, projeyi GitHub'a yüklemek için hızlı adımları içerir.

## ⚡ 5 Dakikada GitHub'a Yükleme

### 1. GitHub'da Repository Oluştur
```bash
# GitHub.com'a git
# Sağ üst + > New repository
# Repository adı: hackathon-scraping
# Public/Private seç
# Create repository
```

### 2. Yerel Git Başlat
```bash
# Proje klasörüne git
cd C:\Users\Furkan\Desktop\HACKATHON\hackathon-scraping

# Git başlat
git init

# GitHub'ı remote olarak ekle (KULLANICI_ADINIZ'ı değiştir)
git remote add origin https://github.com/KULLANICI_ADINIZ/hackathon-scraping.git
```

### 3. Dosyaları Hazırla
```bash
# GitHub klasöründeki dosyaları ana dizine kopyala
copy github\.gitignore .gitignore
copy github\README.md README.md
copy github\LICENSE LICENSE

# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "feat: initial commit - hackathon scraping project"

# Main branch oluştur
git branch -M main
```

### 4. GitHub'a Yükle
```bash
# Push et
git push -u origin main
```

## 🔧 Önemli Dosyalar

### .gitignore
- Gereksiz dosyaları GitHub'a yüklemez
- `github/.gitignore` → ana dizine kopyala

### README.md
- Proje açıklaması
- `github/README.md` → ana dizine kopyala

### LICENSE
- MIT lisansı
- `github/LICENSE` → ana dizine kopyala

## 📁 Yüklenecek Klasörler

✅ **Yüklenecek:**
- `backend/` - Flask API
- `frontend/` - React uygulaması
- `tests/` - Test dosyaları
- `docker-compose.yml`
- `requirements.txt`
- `package.json`

❌ **Yüklenmeyecek:**
- `__pycache__/`
- `node_modules/`
- `.env` dosyaları
- Log dosyaları

## 🚨 Hızlı Çözümler

### Authentication Hatası
```bash
# Personal Access Token kullan
git remote set-url origin https://TOKEN@github.com/KULLANICI_ADINIZ/hackathon-scraping.git
```

### Büyük Dosya Hatası
```bash
# .gitignore'a ekle
echo "*.log" >> .gitignore
echo "*.db" >> .gitignore
```

### Branch Hatası
```bash
git branch -M main
```

## ✅ Kontrol Listesi

- [ ] GitHub repository oluşturuldu
- [ ] Git init yapıldı
- [ ] Remote origin eklendi
- [ ] .gitignore kopyalandı
- [ ] README.md kopyalandı
- [ ] LICENSE kopyalandı
- [ ] İlk commit yapıldı
- [ ] GitHub'a push edildi

## 🎯 Sonraki Adımlar

1. **GitHub Pages** - Web sitesi yayınla
2. **GitHub Actions** - CI/CD pipeline kur
3. **Issues** - Proje yönetimi başlat
4. **Wiki** - Detaylı dokümantasyon ekle

## 📞 Yardım

Sorun yaşarsanız:
- `github/GITHUB_SETUP.md` - Detaylı rehber
- GitHub Docs: https://docs.github.com/
- Git Docs: https://git-scm.com/doc 
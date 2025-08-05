# 🤝 Katkıda Bulunma Rehberi

Bu projeye katkıda bulunmak istediğiniz için teşekkürler! Bu rehber, projeye nasıl katkıda bulunabileceğinizi açıklar.

## 📋 İçindekiler

- [Başlamadan Önce](#başlamadan-önce)
- [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
- [Kod Yazma Kuralları](#kod-yazma-kuralları)
- [Test Yazma](#test-yazma)
- [Pull Request Süreci](#pull-request-süreci)
- [Issue Raporlama](#issue-raporlama)
- [İletişim](#iletişim)

## 🚀 Başlamadan Önce

### Katkıda Bulunabileceğiniz Alanlar

- 🐛 **Bug Fixes**: Hataları düzeltme
- ✨ **New Features**: Yeni özellikler ekleme
- 📚 **Documentation**: Dokümantasyon iyileştirme
- 🧪 **Tests**: Test kapsamını artırma
- 🎨 **UI/UX**: Kullanıcı arayüzü iyileştirmeleri
- ⚡ **Performance**: Performans optimizasyonları
- 🔒 **Security**: Güvenlik iyileştirmeleri

### Katkı Türleri

1. **Bug Report**: Hata raporlama
2. **Feature Request**: Özellik isteği
3. **Code Contribution**: Kod katkısı
4. **Documentation**: Dokümantasyon
5. **Translation**: Çeviri

## 🛠️ Geliştirme Ortamı Kurulumu

### 1. Fork ve Clone

```bash
# GitHub'da projeyi fork edin
# Sonra local'e clone edin
git clone https://github.com/YOUR_USERNAME/hackathon-scraping.git
cd hackathon-scraping

# Upstream remote'u ekleyin
git remote add upstream https://github.com/ORIGINAL_OWNER/hackathon-scraping.git
```

### 2. Sanal Ortam Kurulumu

```bash
# Python sanal ortamı oluşturun
python -m venv .venv

# Sanal ortamı etkinleştirin
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Gereksinimleri yükleyin
pip install -r requirements.txt
```

### 3. Frontend Kurulumu

```bash
# Frontend dizinine gidin
cd frontend

# Node.js bağımlılıklarını yükleyin
npm install

# Development server'ı başlatın
npm start
```

### 4. Veritabanı Kurulumu

```bash
# PostgreSQL'de veritabanı oluşturun
createdb ai_seller_analysis_dev

# pgvector extension'ını etkinleştirin
psql -d ai_seller_analysis_dev -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 5. Ortam Değişkenleri

```bash
# .env dosyası oluşturun
cp .env.example .env

# Gerekli değişkenleri düzenleyin
nano .env
```

## 📝 Kod Yazma Kuralları

### Python Kod Stili

- **PEP 8** standartlarına uyun
- **Black** formatter kullanın
- **isort** ile import'ları sıralayın
- **flake8** ile linting yapın

```bash
# Kod formatlaması
black .
isort .
flake8 .
```

### JavaScript/React Kod Stili

- **ESLint** kurallarına uyun
- **Prettier** ile formatlama yapın
- **TypeScript** kullanımını teşvik edin

```bash
# Frontend kod formatlaması
cd frontend
npm run lint
npm run format
```

### Commit Mesajları

Conventional Commits standardını kullanın:

```
feat: yeni özellik ekle
fix: hata düzelt
docs: dokümantasyon güncelle
style: kod formatlaması
refactor: kod refactoring
test: test ekle
chore: bakım işleri
```

### Branch Naming

```
feature/urun-arama-gelistirme
bugfix/backend-baglanti-hatasi
hotfix/kritik-guvenlik-duzeltmesi
docs/api-dokumantasyonu
```

## 🧪 Test Yazma

### Backend Testleri

```python
# tests/test_new_feature.py
import pytest
from backend.app import app

def test_new_feature():
    """Yeni özellik testi"""
    with app.test_client() as client:
        response = client.get('/api/new-endpoint')
        assert response.status_code == 200
        assert 'data' in response.get_json()

def test_error_handling():
    """Hata yönetimi testi"""
    with app.test_client() as client:
        response = client.get('/api/invalid-endpoint')
        assert response.status_code == 404
```

### Frontend Testleri

```javascript
// frontend/src/__tests__/NewComponent.test.js
import { render, screen } from '@testing-library/react';
import NewComponent from '../components/NewComponent';

test('renders new component', () => {
  render(<NewComponent />);
  const element = screen.getByText(/test/i);
  expect(element).toBeInTheDocument();
});
```

### Test Çalıştırma

```bash
# Backend testleri
pytest

# Frontend testleri
cd frontend
npm test

# Coverage raporu
pytest --cov=./ --cov-report=html
```

## 🔄 Pull Request Süreci

### 1. Branch Oluşturma

```bash
# Main branch'i güncelleyin
git checkout main
git pull upstream main

# Yeni branch oluşturun
git checkout -b feature/your-feature-name
```

### 2. Geliştirme

```bash
# Değişikliklerinizi yapın
# Testleri yazın
# Dokümantasyonu güncelleyin

# Değişiklikleri commit edin
git add .
git commit -m "feat: yeni özellik eklendi"
```

### 3. Test ve Lint

```bash
# Backend testleri
pytest

# Frontend testleri
cd frontend && npm test

# Kod kalitesi kontrolü
black .
isort .
flake8 .
```

### 4. Push ve PR

```bash
# Branch'inizi push edin
git push origin feature/your-feature-name

# GitHub'da Pull Request oluşturun
```

### 5. PR Template

```markdown
## 📝 Açıklama
Bu PR'ın ne yaptığını açıklayın.

## 🎯 Değişiklik Türü
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## 🧪 Testler
- [ ] Backend testleri geçiyor
- [ ] Frontend testleri geçiyor
- [ ] Manuel testler yapıldı

## 📸 Screenshots (UI değişiklikleri için)
<!-- Gerekirse ekran görüntüleri ekleyin -->

## 🔗 İlgili Issue
Closes #123

## ✅ Checklist
- [ ] Kod standartlarına uygun
- [ ] Testler yazıldı
- [ ] Dokümantasyon güncellendi
- [ ] Self-review yapıldı
```

## 🐛 Issue Raporlama

### Bug Report Template

```markdown
## 🐛 Bug Açıklaması
Hatanın ne olduğunu açıklayın.

## 🔄 Tekrar Üretme Adımları
1. '...' sayfasına gidin
2. '....' butonuna tıklayın
3. '....' hatası görünür

## 📱 Beklenen Davranış
Ne olması gerektiğini açıklayın.

## 📸 Screenshots
Varsa ekran görüntüleri ekleyin.

## 💻 Sistem Bilgileri
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 90]
- Version: [e.g. 1.0.0]

## 📋 Ek Bilgiler
Ek bağlam veya log dosyaları.
```

### Feature Request Template

```markdown
## 🚀 Özellik İsteği
İstediğiniz özelliği açıklayın.

## 💡 Çözüm Önerisi
Nasıl çalışmasını istediğinizi açıklayın.

## 🔄 Alternatifler
Düşündüğünüz alternatif çözümler.

## 📋 Ek Bilgiler
Ek bağlam veya örnekler.
```

## 📚 Dokümantasyon

### Kod Dokümantasyonu

```python
def complex_function(param1: str, param2: int) -> dict:
    """
    Karmaşık işlemi gerçekleştirir.
    
    Args:
        param1 (str): İlk parametre açıklaması
        param2 (int): İkinci parametre açıklaması
        
    Returns:
        dict: Sonuç açıklaması
        
    Raises:
        ValueError: Hata durumu açıklaması
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

### API Dokümantasyonu

```python
@app.route('/api/example', methods=['POST'])
def example_endpoint():
    """
    Örnek API endpoint'i.
    
    ---
    tags:
      - Example
    parameters:
      - name: data
        in: body
        required: true
        schema:
          type: object
          properties:
            field1:
              type: string
              description: Açıklama
    responses:
      200:
        description: Başarılı yanıt
      400:
        description: Hatalı istek
    """
    pass
```

## 🔒 Güvenlik

### Güvenlik Açığı Raporlama

Güvenlik açıkları için:
- **Özel email**: security@example.com
- **Gizli issue** oluşturun
- **Responsible disclosure** prensibini uygulayın

### Güvenlik Kontrol Listesi

- [ ] Input validation
- [ ] SQL injection koruması
- [ ] XSS koruması
- [ ] CSRF koruması
- [ ] Authentication/Authorization
- [ ] Sensitive data encryption

## 🌍 Çeviri

### Çeviri Katkısı

```bash
# Çeviri dosyalarını düzenleyin
# frontend/src/locales/tr.json
{
  "common": {
    "save": "Kaydet",
    "cancel": "İptal"
  }
}
```

## 📊 Performans

### Performans Kontrol Listesi

- [ ] Database query optimization
- [ ] Caching implementation
- [ ] Image optimization
- [ ] Bundle size reduction
- [ ] Lazy loading

## 🤝 İletişim

### Topluluk Kanalları

- **Discord**: [Link]
- **Slack**: [Link]
- **Email**: contributors@example.com
- **GitHub Discussions**: [Link]

### Code of Conduct

Bu proje [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct'unu takip eder.

## 🙏 Teşekkürler

Katkıda bulunan herkese teşekkürler! Projeyi daha iyi hale getirmek için çalışıyoruz.

---

**Not**: Bu rehber sürekli güncellenmektedir. Önerileriniz için issue açabilirsiniz. 
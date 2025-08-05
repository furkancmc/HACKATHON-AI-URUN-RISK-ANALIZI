# 🚀 GitHub Repository Kurulum Rehberi

Bu rehber, AI Destekli Satıcı Risk Analiz Sistemi projesini GitHub'a yüklemek için gerekli adımları açıklar.

## 📋 GitHub Repository Hazırlığı

### 1. Repository Oluşturma

1. GitHub'da yeni repository oluşturun
2. Repository adı: `ai-seller-risk-analysis` veya `hackathon-scraping`
3. Açıklama: "AI Destekli Satıcı Risk Analiz Sistemi"
4. Public/Private seçin
5. README, .gitignore ve LICENSE ekleyin

### 2. Repository Ayarları

#### Repository Settings
- **General**: Repository adı ve açıklaması
- **Branches**: Main branch protection rules
- **Pages**: GitHub Pages ayarları (opsiyonel)
- **Security**: Security policy ve vulnerability alerts

#### Branch Protection Rules
```
Branch name pattern: main
Require a pull request before merging: ✓
Require approvals: 1
Dismiss stale PR approvals when new commits are pushed: ✓
Require status checks to pass before merging: ✓
Require branches to be up to date before merging: ✓
```

## 📁 Dosya Yapısı

```
ai-seller-risk-analysis/
├── 📄 README.md                    # Ana proje açıklaması
├── 📄 LICENSE                      # MIT lisansı
├── 📄 CONTRIBUTING.md              # Katkıda bulunma rehberi
├── 📄 DEPLOYMENT.md                # Deployment rehberi
├── 📄 GITHUB_SETUP.md              # Bu dosya
├── 📄 env.example                  # Örnek environment variables
├── 📄 .gitignore                   # Git ignore kuralları
├── 📄 requirements.txt             # Python gereksinimleri
├── 📄 pytest.ini                  # Pytest konfigürasyonu
├── 📄 Dockerfile                   # Backend Docker image
├── 📄 docker-compose.yml           # Docker Compose
├── 📄 setup_pgvector.sql           # PostgreSQL kurulum scripti
├── 📁 .github/
│   └── 📁 workflows/
│       └── 📄 ci.yml              # GitHub Actions CI/CD
├── 📁 backend/
│   ├── 📄 app.py                  # Flask uygulaması
│   └── 📄 requirements.txt        # Backend gereksinimleri
├── 📁 frontend/
│   ├── 📄 package.json            # Node.js bağımlılıkları
│   ├── 📄 Dockerfile              # Frontend Docker image
│   ├── 📄 nginx.conf              # Nginx konfigürasyonu
│   └── 📁 src/                    # React kaynak kodları
├── 📁 tests/
│   ├── 📄 __init__.py             # Test paketi
│   └── 📄 test_backend.py         # Backend testleri
├── 📄 rag_service.py              # RAG servisi
├── 📄 gemini_service.py           # AI servisi
├── 📄 embedding_service.py        # Embedding servisi
├── 📄 create_embeddings.py        # Embedding oluşturma
├── 📄 setup_pgvector.py           # Veritabanı kurulumu
├── 📄 test_system.py              # Sistem testi
├── 📄 start_system.bat            # Windows başlatma
├── 📄 start_system.sh             # Linux başlatma
├── 📄 start_system.ps1            # PowerShell başlatma
└── 📁 data/                       # Veri dosyaları (gitignore)
```

## 🔧 GitHub Features Konfigürasyonu

### 1. Issues Template

`.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows 10]
 - Browser: [e.g. Chrome 90]
 - Version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### 2. Pull Request Template

`.github/pull_request_template.md`:
```markdown
## Description
Brief description of changes

## Type of change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Backend tests pass
- [ ] Frontend tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

### 3. Security Policy

`.github/SECURITY.md`:
```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **Do not** create a public GitHub issue
2. Email us at: security@example.com
3. Include detailed information about the vulnerability
4. We will respond within 48 hours

## Responsible Disclosure

We follow responsible disclosure practices:
- We will acknowledge receipt of your report
- We will investigate and provide updates
- We will work with you to resolve the issue
- We will credit you in our security advisory (if desired)
```

## 🔄 GitHub Actions Secrets

Repository Settings > Secrets and variables > Actions:

### Required Secrets
```
GEMINI_API_KEY=your_gemini_api_key_here
DOCKER_USERNAME=your_docker_username
DOCKER_PASSWORD=your_docker_password
```

### Optional Secrets
```
HOST=your_deployment_host
USERNAME=your_deployment_username
KEY=your_deployment_ssh_key
```

## 📊 Repository Insights

### 1. Insights Tab
- **Traffic**: Repository görüntüleme istatistikleri
- **Commits**: Commit aktivitesi
- **Contributors**: Katkıda bulunanlar
- **Code frequency**: Kod değişim sıklığı

### 2. Settings > Pages
GitHub Pages ile demo site yayınlama:
- Source: Deploy from a branch
- Branch: gh-pages
- Folder: / (root)

### 3. Settings > Integrations
- **Dependabot**: Otomatik dependency güncellemeleri
- **CodeQL**: Güvenlik analizi
- **GitHub Apps**: Ek entegrasyonlar

## 🏷️ Labels ve Milestones

### Labels
```
bug: Hata düzeltmeleri
enhancement: Yeni özellikler
documentation: Dokümantasyon
good first issue: İlk katkı için uygun
help wanted: Yardım gerekli
priority:high: Yüksek öncelik
priority:medium: Orta öncelik
priority:low: Düşük öncelik
```

### Milestones
```
v1.0.0: İlk kararlı sürüm
v1.1.0: Özellik güncellemeleri
v1.2.0: Performans iyileştirmeleri
```

## 📈 Repository Metrics

### 1. Code Quality
- **Code coverage**: Test kapsamı
- **Code climate**: Kod kalitesi
- **SonarCloud**: Kod analizi

### 2. Performance
- **Bundle size**: Frontend bundle boyutu
- **Load time**: Sayfa yükleme süresi
- **API response time**: API yanıt süresi

## 🔗 Badges

README.md'ye eklenecek badge'ler:

```markdown
[![Build Status](https://github.com/username/repo/workflows/CI/badge.svg)](https://github.com/username/repo/actions)
[![Code Coverage](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/username/repo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
```

## 🚀 Release Management

### 1. Release Notes Template
```markdown
## What's Changed
- ✨ New features
- 🐛 Bug fixes
- 📚 Documentation updates
- ⚡ Performance improvements

## Breaking Changes
- None

## Migration Guide
- No migration required

## Contributors
Thanks to all contributors!
```

### 2. Semantic Versioning
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## 📋 Checklist

### Repository Setup
- [ ] Repository oluşturuldu
- [ ] README.md güncellendi
- [ ] LICENSE eklendi
- [ ] .gitignore eklendi
- [ ] CONTRIBUTING.md eklendi
- [ ] DEPLOYMENT.md eklendi

### GitHub Features
- [ ] Issue templates eklendi
- [ ] PR template eklendi
- [ ] Security policy eklendi
- [ ] Branch protection rules ayarlandı
- [ ] GitHub Actions workflow eklendi

### Documentation
- [ ] API dokümantasyonu
- [ ] Kurulum rehberi
- [ ] Kullanım rehberi
- [ ] Troubleshooting rehberi

### Code Quality
- [ ] Test coverage %80+
- [ ] Code linting ayarlandı
- [ ] Pre-commit hooks eklendi
- [ ] Code review guidelines

### Deployment
- [ ] Docker images hazır
- [ ] CI/CD pipeline çalışıyor
- [ ] Production deployment guide
- [ ] Monitoring setup

---

Bu rehber ile GitHub repository'nizi profesyonel bir şekilde kurmuş olacaksınız! 
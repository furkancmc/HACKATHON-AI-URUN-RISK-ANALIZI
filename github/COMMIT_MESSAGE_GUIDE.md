# Commit Mesaj Rehberi

Bu rehber, projede tutarlı commit mesajları yazmanız için hazırlanmıştır.

## 📝 Commit Mesaj Formatı

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

## 🏷️ Type (Tür)

### feat
Yeni özellik ekler
```
feat: add user authentication system
feat(auth): implement JWT token validation
```

### fix
Hata düzeltmesi
```
fix: resolve database connection timeout
fix(api): handle null response from external service
```

### docs
Sadece dokümantasyon değişiklikleri
```
docs: update README installation guide
docs(api): add endpoint documentation
```

### style
Kod stilini etkileyen değişiklikler (formatting, missing semi colons, etc)
```
style: format code according to PEP8
style(frontend): fix indentation in components
```

### refactor
Kodu yeniden düzenleme (bug fix veya feature değil)
```
refactor: extract database connection logic
refactor(utils): simplify date formatting function
```

### test
Test ekleme veya düzenleme
```
test: add unit tests for user service
test(api): add integration tests for product endpoints
```

### chore
Build process veya auxiliary tools değişiklikleri
```
chore: update dependencies
chore: configure CI/CD pipeline
```

### perf
Performans iyileştirmeleri
```
perf: optimize database queries
perf(frontend): reduce bundle size
```

### ci
CI/CD pipeline değişiklikleri
```
ci: add GitHub Actions workflow
ci: update deployment configuration
```

## 🎯 Scope (Kapsam)

Opsiyonel, parantez içinde yazılır. Hangi bölümü etkilediğini belirtir:

- `auth` - Kimlik doğrulama
- `api` - API endpoints
- `frontend` - React uygulaması
- `backend` - Flask uygulaması
- `db` - Veritabanı
- `ui` - Kullanıcı arayüzü
- `utils` - Yardımcı fonksiyonlar

## 📄 Description (Açıklama)

- Kısa ve öz olmalı (50 karakterden az)
- Emir kipi kullanın (add, fix, update, remove)
- İlk harf küçük olmalı
- Nokta ile bitmemeli

## 📝 Body (Gövde)

Opsiyonel, daha detaylı açıklama için:

```
feat: add user authentication system

- Implement JWT token generation
- Add password hashing with bcrypt
- Create login/logout endpoints
- Add middleware for protected routes
```

## 🔗 Footer (Alt Bilgi)

Opsiyonel, issue referansları için:

```
fix: resolve database connection timeout

Closes #123
Fixes #456
```

## ✅ İyi Örnekler

```
feat(auth): add JWT authentication system
fix(api): handle null response from external service
docs: update README with installation guide
refactor(utils): simplify date formatting function
test: add unit tests for user service
chore: update dependencies to latest versions
perf(db): optimize product search queries
```

## ❌ Kötü Örnekler

```
fixed bug
updated code
added feature
changed something
```

## 🔧 Commit Mesajı Yazma Adımları

1. **Değişiklik türünü belirleyin** (feat, fix, docs, etc.)
2. **Kapsamı belirleyin** (opsiyonel)
3. **Kısa açıklama yazın** (50 karakterden az)
4. **Gerekirse body ekleyin** (detaylı açıklama)
5. **Gerekirse footer ekleyin** (issue referansları)

## 🛠️ Git Hooks ile Otomatik Kontrol

Projeye commit hook'u ekleyebilirsiniz:

```bash
# .git/hooks/commit-msg dosyası
#!/bin/sh
commit_regex='^(feat|fix|docs|style|refactor|test|chore|perf|ci)(\(.+\))?: .{1,50}$'

if ! grep -qE "$commit_regex" "$1"; then
    echo "❌ Commit mesajı formatı yanlış!"
    echo "✅ Doğru format: type(scope): description"
    echo "📝 Örnek: feat(auth): add JWT authentication"
    exit 1
fi
```

## 📚 Kaynaklar

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format) 
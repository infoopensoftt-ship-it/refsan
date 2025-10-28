# 🎯 GITHUB ACTIONS KURULUMU - HIZLI BAŞLANGIÇ

## ✅ SİZİN İÇİN HAZIRLADIM

GitHub Actions tamamen kuruldu ve hazır! Şimdi sadece birkaç basit adım kalıyor.

---

## 📝 YAPMANIZ GEREKENLER (5-10 DAKİKA)

### 1️⃣ GitHub Hesabı Açın
https://github.com → Sign up

### 2️⃣ Yeni Repository Oluşturun
- Repository name: `refsan-technical-app`
- ☑️ Private

### 3️⃣ Projeyi GitHub'a Yükleyin

**Git yüklü değilse:** https://git-scm.com/download/win

**Command Prompt'ta:**
```bash
cd C:\Users\pc\Downloads\refsan-main\refsan-main

git config --global user.name "İsminiz"
git config --global user.email "email@ornek.com"

git init
git add .
git commit -m "Refsan Technical App"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADINIZ/refsan-technical-app.git
git push -u origin main
```

**NOT:** `KULLANICI_ADINIZ` yerine GitHub kullanıcı adınızı yazın!

### 4️⃣ GitHub Secrets Ekleyin

Repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

**4 adet secret ekleyin:**

| Name | Value |
|------|-------|
| KEYSTORE_BASE64 | [Aşağıdaki uzun metni kopyalayın] |
| KEYSTORE_PASSWORD | refsan2024 |
| KEY_ALIAS | refsan-key-alias |
| KEY_PASSWORD | refsan2024 |

**KEYSTORE_BASE64 değeri:**
```
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
AicQ
```

**NOT:** Bu metni TAMAMEN kopyalayıp yapıştırın! (3778 karakter)

### 5️⃣ Actions'ı Çalıştırın

Repository → **Actions** → **Build Android AAB** → **Run workflow** → **Run workflow** (yeşil buton)

**Bekleyin:** 10-15 dakika

### 6️⃣ AAB'yi İndirin

Build bitince:
- **Actions** → En son workflow'a tıklayın
- Aşağıda **Artifacts** → **app-release** → İndirin
- ZIP'i açın → **app-release.aab** dosyası hazır!

---

## 🎉 TAMAMLANDI!

AAB dosyasını Play Console'a yükleyebilirsiniz!

---

## 📞 Yardım

Takılırsanız:
1. `GITHUB_ACTIONS_REHBER.md` dosyasına bakın (detaylı açıklamalar)
2. GitHub Actions log'larını kontrol edin
3. Secrets'ları doğru girdiğinizden emin olun

**Başarılar! 🚀**

# 🚀 GitHub Actions ile Otomatik AAB Oluşturma Rehberi

## ✅ HAZIRLIK TAMAMLANDI!

GitHub Actions kurulumu tamamlandı. Artık projeyi GitHub'a her yüklediğinizde otomatik olarak AAB dosyası oluşturulacak!

---

## 📋 ADIM ADIM TALİMATLAR

### ADIM 1: GitHub Hesabı Oluşturun (Eğer Yoksa)

1. https://github.com adresine gidin
2. **Sign up** (Kayıt Ol) butonuna tıklayın
3. Email, kullanıcı adı ve şifre belirleyin
4. Hesabınızı onaylayın

---

### ADIM 2: Yeni Repository (Depo) Oluşturun

1. GitHub'da oturum açın
2. Sağ üstteki **+** simgesine tıklayın
3. **New repository** seçin
4. Bilgileri doldurun:
   ```
   Repository name: refsan-technical-app
   Description: Refsan Technical Service Application
   ☑️ Private (Özel - başkaları göremesin)
   ```
5. **Create repository** tıklayın

---

### ADIM 3: Projeyi GitHub'a Yükleyin

#### Windows Command Prompt'ta:

```bash
cd C:\Users\pc\Downloads\refsan-main\refsan-main

git init

git add .

git commit -m "Initial commit - Refsan Technical App"

git branch -M main

git remote add origin https://github.com/[KULLANICI_ADINIZ]/refsan-technical-app.git

git push -u origin main
```

**NOT:** `[KULLANICI_ADINIZ]` yerine GitHub kullanıcı adınızı yazın!

**Eğer Git yüklü değilse:**
https://git-scm.com/download/win adresinden Git'i indirip kurun.

---

### ADIM 4: GitHub Secrets Ekleyin (ÖNEMLİ!)

GitHub'da repository sayfasında:

1. **Settings** (Ayarlar) sekmesine tıklayın
2. Sol menüden **Secrets and variables** → **Actions** seçin
3. **New repository secret** butonuna tıklayın

**Şu 4 secret'ı ekleyin:**

#### Secret 1: KEYSTORE_BASE64
- Name: `KEYSTORE_BASE64`
- Value: `/app/keystore_base64.txt` dosyasının içeriğini kopyalayın
  (Çok uzun bir metin, tamamını kopyalayın)
- **Add secret** tıklayın

#### Secret 2: KEYSTORE_PASSWORD
- Name: `KEYSTORE_PASSWORD`
- Value: `refsan2024`
- **Add secret** tıklayın

#### Secret 3: KEY_ALIAS
- Name: `KEY_ALIAS`
- Value: `refsan-key-alias`
- **Add secret** tıklayın

#### Secret 4: KEY_PASSWORD
- Name: `KEY_PASSWORD`
- Value: `refsan2024`
- **Add secret** tıklayın

---

### ADIM 5: GitHub Actions'ı Çalıştırın

1. Repository ana sayfasında **Actions** sekmesine tıklayın
2. "Build Android AAB" workflow'unu göreceksiniz
3. **Run workflow** butonuna tıklayın
4. **Run workflow** (yeşil buton) tıklayın
5. **Bekleyin** (10-15 dakika)

---

### ADIM 6: AAB Dosyasını İndirin

Build tamamlandıktan sonra:

1. **Actions** sekmesinde en son çalışan workflow'a tıklayın
2. Aşağıda **Artifacts** (Yapılar) bölümünde `app-release` göreceksiniz
3. **app-release** üzerine tıklayarak ZIP dosyasını indirin
4. ZIP'i açın, içinde `app-release.aab` dosyası var!
5. **Bu dosyayı Play Console'a yükleyin!**

---

## 🎉 TAMAMLANDI!

Artık:
- ✅ Her kod değişikliğinde otomatik AAB oluşur
- ✅ AAB dosyasını 30 gün boyunca indirebilirsiniz
- ✅ Hiçbir kurulum gerektirmez
- ✅ Tamamen ücretsiz!

---

## 🔄 Sonraki Güncellemeler İçin

Uygulama güncelleyecekseniz:

1. `frontend/android/app/build.gradle` dosyasında versiyonu artırın:
   ```gradle
   versionCode 2  // +1 artırın
   versionName "1.1"
   ```

2. Değişiklikleri GitHub'a yükleyin:
   ```bash
   git add .
   git commit -m "Version 1.1 update"
   git push
   ```

3. Actions otomatik çalışacak!

---

## ⚠️ ÖNEMLİ NOTLAR

### Keystore Base64 Dosyası

`/app/keystore_base64.txt` dosyasının içeriği çok uzun (yaklaşık 3800 karakter).

**Nasıl kopyalanır:**

Linux/Mac:
```bash
cat /app/keystore_base64.txt
```

**Tüm çıktıyı kopyalayıp GitHub Secret'a yapıştırın!**

### Git Kullanıcı Ayarları

İlk kez Git kullanıyorsanız:
```bash
git config --global user.name "İsminiz"
git config --global user.email "email@example.com"
```

### GitHub Token (Eğer Şifre İstemiyorsa)

GitHub artık şifre yerine Personal Access Token istiyor:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Generate new token** (classic)
3. Seçenekler:
   - Note: `Refsan App`
   - Expiration: `90 days`
   - ☑️ repo (tüm alt seçenekler)
4. **Generate token**
5. Token'ı kopyalayın (BİR DAHA GÖREMEZSİNİZ!)
6. Git push yaparken şifre yerine bu token'ı kullanın

---

## 🆘 Sorun Giderme

### "Git is not recognized"
→ Git'i kurun: https://git-scm.com/download/win

### "Repository not found"
→ Repository adını ve kullanıcı adını kontrol edin

### "Authentication failed"
→ Personal Access Token kullanın (yukarıda açıklandı)

### "Build failed in Actions"
→ Secrets'ları doğru eklediniz mi kontrol edin

### "Keystore not found"
→ KEYSTORE_BASE64 secret'ını doğru yapıştırdınız mı kontrol edin

---

## 📞 Destek

Herhangi bir adımda takılırsanız:
1. GitHub Actions log'larını kontrol edin (hata mesajları orada)
2. Secrets'ların doğru girildiğini doğrulayın
3. Projenin düzgün yüklendiğini kontrol edin

---

**Başarılar! 🚀**

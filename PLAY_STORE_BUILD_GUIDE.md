# 📱 Refsan Technical - Play Store Yükleme Rehberi

## 🔑 Keystore Bilgileri (ÇOK ÖNEMLİ!)

**⚠️ BU BİLGİLERİ GÜVENLİ BİR YERDE SAKLAYIN!**

```
Keystore Dosyası: refsan-release-key.keystore
Lokasyon: frontend/android/app/refsan-release-key.keystore
Store Password: refsan2024
Key Alias: refsan-key-alias
Key Password: refsan2024
```

**UYARI:** Bu keystore'u kaybederseniz uygulamanızı Play Store'da güncelleyemezsiniz!

---

## 🚀 Build Adımları (Local Bilgisayarda)

### Gereksinimler:
- Node.js (v14 veya üzeri)
- Android Studio (Android SDK ile birlikte)
- Java JDK 11 veya üzeri

### Adım 1: Bağımlılıkları Kurun

```bash
cd frontend
npm install
```

### Adım 2: Production Build

```bash
npm run build
```

### Adım 3: Capacitor Sync

```bash
npx cap sync android
```

### Adım 4: Android Studio'da Aç

```bash
npx cap open android
```

---

## 🏗️ AAB Oluşturma (Play Store için)

### Yöntem 1: Android Studio (Kolay)

1. Android Studio menüsünden: **Build** → **Generate Signed Bundle / APK**
2. **Android App Bundle** seçin, **Next**
3. Keystore bilgilerini girin:
   - Key store path: `app/refsan-release-key.keystore`
   - Key store password: `refsan2024`
   - Key alias: `refsan-key-alias`
   - Key password: `refsan2024`
4. **Next** → **release** seçin → **Create**

**Çıktı:** `android/app/build/outputs/bundle/release/app-release.aab`

### Yöntem 2: Komut Satırı

```bash
cd frontend/android
./gradlew bundleRelease
```

**Çıktı:** `app/build/outputs/bundle/release/app-release.aab`

---

## 📦 APK Oluşturma (Test için)

Play Store AAB ister, ama test için APK oluşturabilirsiniz:

```bash
cd frontend/android
./gradlew assembleRelease
```

**Çıktı:** `app/build/outputs/apk/release/app-release.apk`

---

## 🎯 Play Store'a Yükleme

### 1. Google Play Console'a Gidin
https://play.google.com/console

### 2. Yeni Uygulama Oluşturun
- "Create app" butonuna tıklayın
- Uygulama adı: **Refsan Technical**
- Varsayılan dil: **Türkçe**
- Uygulama veya oyun: **Uygulama**
- Ücretsiz veya ücretli: **Ücretsiz**

### 3. Uygulama Detayları
- Kısa açıklama (80 karakter)
- Tam açıklama (4000 karakter)
- Ekran görüntüleri (en az 2 adet, telefon için)
- Uygulama simgesi (512x512 PNG)

### 4. İçerik Derecelendirmesi
- Anketi doldurun
- Yaş sınırı belirlenecek

### 5. Hedef Kitle
- Hedef yaş grubu seçin
- Çocuklara yönelik değilse belirtin

### 6. Production'a Yükle
- **Production** → **Create new release**
- AAB dosyasını yükleyin
- Sürüm notları ekleyin (örn: "İlk sürüm")
- **Review release** → **Start rollout**

### 7. İnceleme Süreci
- Google inceleme süreci 1-7 gün sürebilir
- Onaylandıktan sonra Play Store'da yayınlanır

---

## 📝 Uygulama Bilgileri

```
Package ID: com.refsan.technical
App Name: Refsan Technical
Version: 1.0 (versionCode 1)
Min SDK: API 22 (Android 5.1)
Target SDK: API 34 (Android 14)
```

---

## 🔄 Güncelleme Yaparken

Her güncelleme için:

1. `build.gradle` içinde `versionCode` ve `versionName` artırın:
```gradle
versionCode 2  // Her güncellemede +1 artırın
versionName "1.1"  // Kullanıcılara gösterilen versiyon
```

2. Yeni AAB oluşturun (aynı keystore ile!)
3. Play Console'da yeni release oluşturun
4. AAB'yi yükleyin

---

## ⚠️ Önemli Notlar

1. **Keystore'u Yedekleyin:** 
   - Keystore dosyasını güvenli bir yerde saklayın
   - Şifrelerini not edin
   - Kaybederseniz uygulamayı güncelleyemezsiniz!

2. **Test Edin:**
   - Play Store'a yüklemeden önce APK'yı test cihazda deneyin
   - Internal testing kullanarak beta test yapabilirsiniz

3. **İçerik Politikası:**
   - Google Play Store politikalarına uyun
   - Gizlilik politikası URL'i gerekebilir

4. **Ekran Görüntüleri:**
   - En az 2 ekran görüntüsü gerekli
   - Boyut: 320-3840 px arası
   - Format: PNG veya JPEG

---

## 🆘 Sorun Giderme

### Build Hatası: "SDK location not found"
```bash
# Android Studio'da Android SDK yolunu ayarlayın
# Veya local.properties dosyasına ekleyin:
sdk.dir=/Users/USERNAME/Library/Android/sdk  # Mac
sdk.dir=C:\\Users\\USERNAME\\AppData\\Local\\Android\\Sdk  # Windows
```

### Build Hatası: "Keystore not found"
- Keystore dosyasının `android/app/` klasöründe olduğundan emin olun
- Şifreleri kontrol edin

### APK/AAB Bulamıyorum
- `android/app/build/outputs/` klasörüne bakın
- Build log'larında "BUILD SUCCESSFUL" mesajını kontrol edin

---

## 📞 Destek

Sorularınız için:
- Android Studio dökümantasyonu: https://developer.android.com
- Capacitor dökümantasyonu: https://capacitorjs.com
- Play Console yardım: https://support.google.com/googleplay

---

**İyi Şanslar! 🚀**

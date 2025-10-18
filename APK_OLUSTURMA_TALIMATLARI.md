# 📱 Refsan Technical Service - Android APK Oluşturma Rehberi

## ✅ Hazırlık Tamamlandı!

Android projesi tamamen hazır ve test edilmeye hazır! İşte APK oluşturma yolları:

---

## 🚀 YÖNTEM 1: GitHub Repository'den Build (ÖNERİLEN)

### Adım 1: Projeyi GitHub'a Push Edin

```bash
cd /app
git add .
git commit -m "Android app ready for build"
git push origin main
```

### Adım 2: Bilgisayarınıza Clone Edin

```bash
git clone https://github.com/your-username/refsan.git
cd refsan/frontend
```

### Adım 3: Android Studio ile APK Build

1. **Android Studio'yu açın**
   - Download: https://developer.android.com/studio

2. **Projeyi açın**
   - File → Open → `refsan/frontend/android` klasörünü seçin

3. **Gradle Sync bekleyin** (ilk seferde 5-10 dakika sürebilir)

4. **APK Build edin**
   - Build → Build Bundle(s) / APK(s) → Build APK(s)
   - Ya da menüden: Build → Build APK

5. **APK dosyasını bulun**
   - `frontend/android/app/build/outputs/apk/debug/app-debug.apk`

6. **Telefona kurun**
   - USB ile bağlayın veya dosyayı paylaşın
   - "Bilinmeyen Kaynaklardan Kurulum" iznini verin
   - APK'yı kurun

---

## 🖥️ YÖNTEM 2: Doğrudan Gradle ile (Terminal)

### Gereksinimler:
- Java JDK 17+ 
- Android SDK (Android Studio otomatik kurar)

### Komutlar:

```bash
# 1. Projeyi klonlayın
git clone https://github.com/your-username/refsan.git
cd refsan/frontend

# 2. Build yapın
cd android
./gradlew assembleDebug

# 3. APK yolu
# android/app/build/outputs/apk/debug/app-debug.apk
```

---

## 🌐 YÖNTEM 3: PWA (Hemen Test Edin!)

APK beklemeden şimdi test edin:

1. **Telefonda Chrome'u açın**
2. **Uygulamanın URL'ine gidin:** https://your-app-url.com
3. **Menü:** ⋮ → "Ana ekrana ekle"
4. **Uygulama simgesi ekrana eklenir!**

✅ Tam ekran çalışır
✅ Uygulama gibi davranır
✅ Offline çalışabilir

---

## 📦 Proje Yapısı

```
/app/
├── frontend/
│   ├── android/              # Android projesi (Capacitor)
│   │   ├── app/
│   │   │   └── build/
│   │   │       └── outputs/
│   │   │           └── apk/
│   │   │               └── debug/
│   │   │                   └── app-debug.apk  ← APK BURAYA ÜRETİLİR
│   │   ├── gradle/
│   │   ├── gradlew           # Gradle wrapper
│   │   └── local.properties  # SDK yolu
│   ├── build/                # React build çıktısı
│   ├── src/                  # React kaynak kodları
│   ├── public/               # HTML sayfaları
│   └── capacitor.config.json # Capacitor ayarları
└── backend/                  # FastAPI backend

```

---

## 🔧 Sorun Giderme

### Gradle Build Hatası?

```bash
# SDK konumunu ayarlayın
echo "sdk.dir=/path/to/Android/sdk" > android/local.properties
```

### Android Studio'da Sync Hatası?

1. File → Invalidate Caches / Restart
2. Tools → SDK Manager → Android 13 (API 33) yüklü olduğundan emin olun

### APK Kurulamıyor?

1. Ayarlar → Güvenlik → "Bilinmeyen Kaynaklardan" aktif
2. Ya da: Ayarlar → Uygulamalar → Chrome → İzinlerini yönet

---

## 📱 APK Bilgileri

- **Uygulama Adı:** Refsan Technical
- **Paket Adı:** com.refsan.technical
- **Minimum Android:** 5.1 (API 22)
- **Hedef Android:** 13 (API 33)
- **APK Boyutu:** ~8-12 MB (debug)
- **İmzalama:** Debug (test için), Release için keystore gerekir

---

## 🎯 Release APK (Production) Oluşturma

Production için imzalı APK:

```bash
# 1. Keystore oluştur (bir kez)
keytool -genkey -v -keystore refsan.keystore -alias refsan -keyalg RSA -keysize 2048 -validity 10000

# 2. gradle.properties'e ekle
REFSAN_RELEASE_STORE_FILE=../refsan.keystore
REFSAN_RELEASE_KEY_ALIAS=refsan
REFSAN_RELEASE_STORE_PASSWORD=your_password
REFSAN_RELEASE_KEY_PASSWORD=your_password

# 3. Release build
./gradlew assembleRelease

# APK: android/app/build/outputs/apk/release/app-release.apk
```

---

## 📞 Destek

Sorun yaşarsanız:
1. GitHub Issues açın
2. Build loglarını paylaşın (`--stacktrace` ile)
3. Android Studio versiyonunu belirtin

---

## ✅ Checklist

- [ ] GitHub'a push edildi
- [ ] Android Studio kuruldu
- [ ] Proje açıldı ve sync tamamlandı
- [ ] APK build edildi
- [ ] Telefona kuruldu
- [ ] Uygulama test edildi

---

**🎉 Başarılar! Sorularınız için GitHub Issues'u kullanın.**

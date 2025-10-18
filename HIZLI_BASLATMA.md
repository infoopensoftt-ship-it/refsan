# ⚡ HIZLI BAŞLATMA - 5 DAKİKADA APK

## 🎯 EN HIZLI YOL

### 1️⃣ Projeyi İndir
```bash
# Emergent'ten "Download Project" veya GitHub'dan clone
```

### 2️⃣ Android Studio'da Aç
```
File → Open → refsan/frontend/android klasörünü seç
```

### 3️⃣ Gradle Sync Bekle
```
Alt panelde "Gradle Sync" tamamlanana kadar bekle (5-10 dk)
```

### 4️⃣ APK Oluştur
```
Build → Build Bundle(s) / APK(s) → Build APK(s)
```

### 5️⃣ APK'yı Bul
```
android/app/build/outputs/apk/debug/app-debug.apk
```

### 6️⃣ Telefona Kur
```
APK'yı telefona gönder → Kur
```

---

## 🚨 İLK KEZ Mİ?

### Android Studio İlk Kurulum:

1. **Android Studio'yu aç**

2. **SDK Manager'ı kontrol et:**
   - Tools → SDK Manager
   - Android 13.0 (API 33) işaretle
   - Apply

3. **İlk sync uzun sürer:**
   - 5-10 dakika bekle
   - Kahve iç ☕

---

## 📱 TELEFONA KURULUM

### A) USB ile (En Hızlı)
```
1. USB kablosu tak
2. APK'yı telefona kopyala
3. Telefonda APK'ya tıkla
4. "Bilinmeyen Kaynaklar" izni ver
5. Kur!
```

### B) Android Studio'dan Direkt
```
1. USB kablosu tak
2. Telefonda USB Debugging aç
3. Android Studio'da: Run → Run 'app'
4. Telefonunu seç
5. Otomatik kurar!
```

---

## ⚡ KOMUTLARLA (Terminal)

```bash
# 1. Klasöre git
cd refsan/frontend/android

# 2. APK oluştur
./gradlew assembleDebug

# 3. APK hazır!
# android/app/build/outputs/apk/debug/app-debug.apk
```

---

## ❌ HATA ALDIM?

### "SDK not found"
```
Tools → SDK Manager → Android 13.0 kur
```

### "Gradle sync failed"
```
File → Invalidate Caches → Restart
```

### "Build failed"
```
Build → Clean Project
Build → Rebuild Project
```

---

## ✅ TESTİM HAZIR!

APK oluştu ve telefonda çalışıyor! 🎉

**Test Kullanıcıları:**
- Admin: admin@demo.com / admin123
- Teknisyen: teknisyen@demo.com / test123

---

## 🎯 SONRAKI ADIM: RELEASE APK

Production için imzalı APK:

```
Build → Generate Signed Bundle / APK
→ APK → Create new keystore
→ Bilgileri doldur → Finish
```

Release APK Google Play'e yüklenebilir!

---

Her şey hazır! Kolay gelsin! 🚀

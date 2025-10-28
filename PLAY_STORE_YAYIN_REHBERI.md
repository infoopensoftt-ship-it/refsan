# 📱 Google Play Store'da Uygulama Yayımlama Rehberi

## 🎯 Önkoşullar

### 1. Google Play Console Hesabı Açma

**Adım 1:** https://play.google.com/console adresine gidin

**Adım 2:** Google hesabınızla giriş yapın

**Adım 3:** Geliştirici Kaydı Yapın
- İlk kez kullanıyorsanız "Get Started" butonuna tıklayın
- Geliştirici sözleşmesini okuyun ve kabul edin
- **25$ tek seferlik kayıt ücreti** ödemeniz gerekecek (kredi kartı)
- Geliştirici hesap bilgilerini doldurun:
  - Geliştirici adı
  - E-posta adresi
  - Telefon numarası
  - Adres bilgileri

**Not:** Kayıt onayı birkaç saat sürebilir.

---

## 📦 Adım 1: AAB Dosyası Hazırlama

### Local Bilgisayarınızda (Windows/Mac/Linux):

```bash
# Terminal/Command Prompt açın

# 1. Proje klasörüne gidin
cd refsan-project/frontend

# 2. Bağımlılıkları kurun
npm install

# 3. Production build yapın
npm run build

# 4. Capacitor sync
npx cap sync android

# 5. Android Studio'da açın
npx cap open android
```

### Android Studio'da AAB Oluşturma:

**1.** Android Studio açıldığında, üst menüden:
   - **Build** → **Generate Signed Bundle / APK** seçin

**2.** Açılan pencerede:
   - **Android App Bundle** seçeneğini işaretleyin
   - **Next** butonuna tıklayın

**3.** Keystore bilgilerini girin:
   ```
   Key store path: [Browse ile refsan-release-key.keystore dosyasını seçin]
   Key store password: refsan2024
   Key alias: refsan-key-alias
   Key password: refsan2024
   ```
   - **Next** butonuna tıklayın

**4.** Build türü seçimi:
   - **release** seçeneğini işaretleyin
   - **Finish** butonuna tıklayın

**5.** Build tamamlandığında:
   - Sağ alt köşede "locate" linki çıkacak, tıklayın
   - Veya manuel olarak gidin: `frontend/android/app/build/outputs/bundle/release/`
   - **app-release.aab** dosyasını bulacaksınız

**6.** Bu dosyayı masaüstüne kopyalayın (kolay erişim için)

---

## 🎨 Adım 2: Görsel Malzemeleri Hazırlama

Play Store'a yüklemeden önce şunları hazırlayın:

### A) Uygulama İkonu (Zorunlu)
- **Boyut:** 512x512 px
- **Format:** PNG (şeffaflık olabilir)
- **İçerik:** Refsan logosu veya uygulama logosu

### B) Feature Graphic (Zorunlu)
- **Boyut:** 1024x500 px
- **Format:** PNG veya JPEG
- **İçerik:** Uygulama tanıtım görseli

### C) Ekran Görüntüleri (Zorunlu - En az 2 adet)
- **Boyut:** 320-3840 px arası (genişlik veya yükseklik)
- **Format:** PNG veya JPEG
- **İçerik:** Uygulamanın farklı ekranları
- **Önerilen ekranlar:**
  1. Login ekranı
  2. Admin paneli ana sayfası
  3. Arıza kayıt formu
  4. Müşteri listesi
  5. Yedek parça seçimi ekranı

**Nasıl Ekran Görüntüsü Alınır:**
- Uygulamayı telefonunuzda açın veya Android Studio emulator'ünde çalıştırın
- Her önemli ekrandan screenshot alın
- Bilgisayara aktarın

---

## 🚀 Adım 3: Play Console'da Uygulama Oluşturma

### 1. Yeni Uygulama Oluşturma

**a)** https://play.google.com/console adresine gidin

**b)** Sol üst köşede "Create app" butonuna tıklayın

**c)** Uygulama detaylarını doldurun:

**App name (Uygulama adı):**
```
Refsan Technical
```

**Default language (Varsayılan dil):**
```
Turkish - Türkçe
```

**App or game (Uygulama veya oyun):**
```
☑️ App (Uygulama)
```

**Free or paid (Ücretsiz veya ücretli):**
```
☑️ Free (Ücretsiz)
```

**d)** Beyanları işaretleyin:
- ☑️ Developer Program Policies'i okudum ve kabul ediyorum
- ☑️ US export laws'a uyuyorum

**e)** **Create app** butonuna tıklayın

---

## 📝 Adım 4: Dashboard Görevlerini Tamamlama

Uygulama oluşturulduktan sonra Dashboard'da yapılması gereken görevler listesi görünecek:

### 1️⃣ Set up your app (Uygulamayı Kurun)

#### A) App access (Uygulama Erişimi)

**Sol menüden:** Policy → App access

**Seçenekler:**
```
☑️ All functionality is available without any access restrictions
   (Tüm işlevlere herkes erişebilir)
```

**Eğer giriş gerekiyorsa:**
```
☑️ All or some functionality is restricted
```
- Test hesabı bilgileri sağlayın:
  ```
  Email: admin@demo.com
  Password: admin123
  Açıklama: Admin test hesabı
  ```

**Save** butonuna tıklayın

---

#### B) Ads (Reklamlar)

**Sol menüden:** Policy → Ads

**Soru:** "Does your app contain ads?"

```
☑️ No, my app does not contain ads
   (Hayır, uygulamam reklam içermez)
```

**Save** butonuna tıklayın

---

#### C) Content ratings (İçerik Derecelendirmesi)

**Sol menüden:** Policy → Content ratings

**1.** **Start questionnaire** butonuna tıklayın

**2.** Email adresi:
```
[İletişim için e-posta adresiniz]
```

**3.** Kategori seçin:
```
☑️ Utility, Productivity, Communication, or Other
   (Araç, Verimlilik, İletişim veya Diğer)
```

**4.** Anket sorularını cevaplayın:
- Does your app contain any violent content? → **No**
- Does your app feature any sexual content? → **No**
- Does your app contain any language some would consider profane? → **No**
- Does your app feature any discrimination-based content? → **No**
- Does your app contain any controlled substances? → **No**
- Does your app contain any gambling content? → **No**

**5.** **Save** → **Calculate rating** tıklayın

**6.** Derecelendirme sonucu görünecek (genelde EVERYONE / PEGI 3)

**7.** **Apply rating** butonuna tıklayın

---

#### D) Target audience (Hedef Kitle)

**Sol menüden:** Policy → Target audience

**1.** Yaş grubu seçin:
```
☑️ 18 and over (18 ve üzeri)
```

**2.** "Is your app primarily directed at children?" sorusu:
```
☑️ No (Hayır)
```

**3.** **Save** butonuna tıklayın

---

#### E) News app (Haber Uygulaması)

**Sol menüden:** Policy → News app

```
☑️ No, it's not a news app
   (Hayır, haber uygulaması değil)
```

**Save** butonuna tıklayın

---

#### F) COVID-19 contact tracing and status apps

**Sol menüden:** Policy → COVID-19 contact tracing

```
☑️ This is not a COVID-19 contact tracing or status app
   (COVID-19 takip uygulaması değil)
```

**Save** butonuna tıklayın

---

#### G) Data safety (Veri Güvenliği)

**Sol menüden:** Policy → Data safety

**1.** **Start** butonuna tıklayın

**2.** "Does your app collect or share any of the required user data types?"

```
☑️ Yes, my app collects or shares user data
   (Evet, uygulama kullanıcı verisi topluyor)
```

**3.** Toplanan veriler (Refsan Technical için):

**Personal info:**
- ☑️ Name (İsim) - Collected, Not shared
- ☑️ Email address (E-posta) - Collected, Not shared
- ☑️ Phone number (Telefon) - Collected, Not shared

**App activity:**
- ☑️ App interactions (Uygulama etkileşimleri) - Collected, Not shared

**4.** Data usage and handling:
- **Is this data collected or shared?** → Collected
- **Is data collection optional or required?** → Required
- **What is this data used for?** → App functionality
- **Is the data encrypted in transit?** → Yes
- **Can users request data deletion?** → Yes

**5.** **Save** → **Submit** tıklayın

---

#### H) Government apps

```
☑️ No, this is not a government app
```

**Save** butonuna tıklayın

---

#### I) Financial features

```
☑️ No, my app does not have financial features
```

**Save** butonuna tıklayın

---

#### J) Health

```
☑️ No, my app does not have health features
```

**Save** butonuna tıklayın

---

### 2️⃣ Store settings (Mağaza Ayarları)

#### A) App category (Uygulama Kategorisi)

**Sol menüden:** Grow → Store presence → Main store listing → scroll down

**App category:**
```
Business (İş)
```

**Store listing contact details:**
```
Email: [destek e-postanız]
Phone: [telefon numaranız] (opsiyonel)
Website: https://refsan-repairs-1.emergent.host (opsiyonel)
```

**Save** butonuna tıklayın

---

#### B) Store listing (Mağaza Listeleme)

**Sol menüden:** Grow → Store presence → Main store listing

**App name:**
```
Refsan Technical Service
```

**Short description (80 karakter max):**
```
Refsan fırınları için teknik servis ve arıza takip uygulaması
```

**Full description (4000 karakter max):**
```
Refsan Technical Service Uygulaması

Refsan marka endüstriyel fırınlarınız için özel olarak geliştirilmiş teknik servis ve arıza takip uygulaması.

ÖZELLİKLER:

🔧 Arıza Kayıt Sistemi
• Hızlı ve kolay arıza bildirimi
• Fotoğraf ve dosya ekleme
• Öncelik seviyesi belirleme
• Gerçek zamanlı durum takibi

📊 Yönetim Paneli
• Tüm arızaları tek ekrandan görüntüleme
• Teknisyen atama ve yönetim
• Müşteri kayıt sistemi
• Detaylı raporlama

💰 Maliyet Yönetimi
• Euro ve TL cinsinden fiyatlandırma
• Otomatik KDV hesaplama
• Mesafe bazlı servis bedeli
• Yedek parça seçimi ve fiyatlandırma

🛠️ Yedek Parça Sistemi
• 50+ yedek parça kataloğu
• Arama ve filtreleme
• Fiyat görüntüleme
• Sipariş takibi

📱 Kullanıcı Tipleri
• Admin: Tam yetki ve sistem yönetimi
• Teknisyen: Arıza takibi ve müşteri yönetimi
• Müşteri: Arıza bildirimi ve takip

🔐 Güvenlik
• Kullanıcı onay sistemi
• Güvenli giriş
• Rol tabanlı erişim kontrolü

Refsan endüstriyel fırınlarınızın bakım ve onarımını kolaylaştırın!
```

**App icon (512x512 PNG):**
- **Upload icon** butonuna tıklayın
- Hazırladığınız 512x512 ikonu yükleyin

**Feature graphic (1024x500):**
- **Upload graphic** butonuna tıklayın
- Hazırladığınız 1024x500 görseli yükleyin

**Phone screenshots (2-8 adet):**
- **Upload screenshots** butonuna tıklayın
- En az 2 ekran görüntüsü yükleyin
- Önerilen sıralama:
  1. Login ekranı
  2. Dashboard/Ana sayfa
  3. Arıza kayıt formu
  4. Yedek parça seçimi
  5. Müşteri listesi

**7-inch tablet screenshots (Opsiyonel)**
**10-inch tablet screenshots (Opsiyonel)**

**Save** butonuna tıklayın

---

### 3️⃣ Select countries and regions (Ülke Seçimi)

**Sol menüden:** Release → Production → Countries/regions

**1.** **Add countries/regions** butonuna tıklayın

**2.** Seçenekler:
```
☑️ All countries (Tüm ülkeler) - Önerilen

VEYA

☑️ Specific countries (Belirli ülkeler)
   Türkiye seçebilirsiniz
```

**3.** **Add countries** butonuna tıklayın

---

## 🎬 Adım 5: İlk Sürümü Yayına Alma

### Production Track'e Yükleme

**1.** Sol menüden: **Release → Production**

**2.** **Create new release** butonuna tıklayın

**3.** **Upload** butonuna tıklayın

**4.** Hazırladığınız **app-release.aab** dosyasını seçin ve yükleyin

**5.** Yükleme tamamlandıktan sonra:
   - Version: 1 (1.0) görünecek
   - Package: com.refsan.technical

**6.** **Release name:**
```
Versiyon 1.0 - İlk Sürüm
```

**7.** **Release notes (Sürüm notları):**
```
tr-TR (Türkçe):
İlk sürüm - Temel özellikler:
• Arıza kayıt sistemi
• Yedek parça yönetimi
• Kullanıcı onay sistemi
• Maliyet hesaplama
• Admin paneli
```

**8.** **Review release** butonuna tıklayın

**9.** Kontrol listesini gözden geçirin:
   - ✅ App bundle uploaded
   - ✅ Store listing complete
   - ✅ Content rating set
   - ✅ Target audience selected
   - ✅ Data safety info provided

**10.** **Start rollout to Production** butonuna tıklayın

**11.** Onay penceresi açılacak, **Rollout** butonuna tıklayın

---

## ⏳ Adım 6: İnceleme Süreci

### Google İnceleme Aşaması

**1.** Uygulama "Pending publication" (Yayın bekliyor) durumuna geçecek

**2.** İnceleme süresi: **1-7 gün** (genelde 2-3 gün)

**3.** İnceleme sırasında Google:
   - Uygulamanın çalıştığını test eder
   - Politikalara uygunluğunu kontrol eder
   - Güvenlik taraması yapar
   - İçerik denetimi yapar

**4.** E-posta bildirimleri alacaksınız:
   - "Your app is being reviewed"
   - "Your app was approved" veya "Changes required"

---

## ✅ Adım 7: Yayınlandı!

### Onaylandıktan Sonra

**1.** E-posta ile bildirim gelecek: "Your app is now available on Google Play"

**2.** Play Console'da durum: **Published** (Yayında)

**3.** Uygulamanız Play Store'da görünmesi: **Birkaç saat sürebilir**

**4.** Uygulama linkiniz:
```
https://play.google.com/store/apps/details?id=com.refsan.technical
```

**5.** Bu linki müşterilerinizle paylaşabilirsiniz!

---

## 📊 Adım 8: Yayın Sonrası

### İstatistikleri Takip Etme

**Sol menüden:** Statistics

- **Overview:** Genel bakış
- **User acquisition:** Kullanıcı edinimi
- **User engagement:** Kullanıcı etkileşimi
- **Crashes and ANRs:** Çökmeler ve hatalar
- **Ratings and reviews:** Puanlar ve yorumlar

### Kullanıcı Yorumlarına Cevap Verme

**Sol menüden:** Reviews

- Kullanıcı yorumlarını okuyun
- Yanıt yazabilirsiniz
- Sorunları çözün

### Uygulama Güncelleme

Yeni versiyon yüklemek için:

**1.** `build.gradle` dosyasında versiyonu artırın:
```gradle
versionCode 2  // +1 artırın
versionName "1.1"
```

**2.** Yeni AAB oluşturun (aynı keystore ile!)

**3.** **Release → Production → Create new release**

**4.** Yeni AAB'yi yükleyin

**5.** Release notes yazın

**6.** **Start rollout** yapın

---

## ⚠️ Sık Karşılaşılan Sorunlar

### 1. "App rejected - Violates policies"

**Çözüm:**
- Reddedilme sebebini okuyun
- Gerekli değişiklikleri yapın
- Yeni AAB yükleyip tekrar gönderin

### 2. "Signing key mismatch"

**Çözüm:**
- Aynı keystore dosyasını kullandığınızdan emin olun
- Şifreleri kontrol edin

### 3. "Store listing incomplete"

**Çözüm:**
- Dashboard'daki tüm görevleri tamamlayın
- Eksik alanları doldurun

### 4. "Screenshots required"

**Çözüm:**
- En az 2 telefon ekran görüntüsü yükleyin
- Doğru boyutta (320-3840 px) olduğundan emin olun

---

## 📞 Yardım ve Destek

### Google Play Console Yardım Merkezi
https://support.google.com/googleplay/android-developer

### Politika Dokümantasyonu
https://play.google.com/about/developer-content-policy/

### Teknik Yardım
https://developer.android.com/distribute

---

## 🎉 Tebrikler!

Uygulamanız artık Google Play Store'da yayında!

**Önemli Hatırlatmalar:**
- ✅ Keystore dosyanızı yedekleyin
- ✅ Kullanıcı yorumlarını takip edin
- ✅ Düzenli güncellemeler yapın
- ✅ İstatistikleri kontrol edin
- ✅ Politika değişikliklerini takip edin

**İyi şanslar! 🚀**

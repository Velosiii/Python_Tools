# - -- Python Tools -- -
## Python ile geliştirdiğim çeşitli araçlar
*Kendimce günlük işleri kolaylaştıran araçlar, genel bug fix ve optimizasyonları yapıldı (Sanırım)*
*   **Pdf ekle çıkar (YoRHa temalı versiyon)**
*   **Instagram profil yedekleyicisi**

---

# YoRHa System Data Manager (PDF Aracı) ⚔️
*For the Glory of Mankind.*

Bu proje, NieR: Automata evreninin ikonik **YoRHa OS** arayüzünden ilham alınarak geliştirilmiş, güçlü ve şık bir masaüstü PDF yönetim aracıdır. Geleneksel sıkıcı araçların aksine; yüksek çözünürlüklü önizleme, sürükle-bırak desteği ve asenkron animasyonlu "Tech" yükleme ekranı ile kullanıcılara benzersiz bir deneyim sunar.

## 🎥 Sistem Önizlemesi
*(Aşağıdaki videoyu oynatarak arayüzü ve işlemleri inceleyebilirsiniz)*

<p align="center">
  <img src="Pdf/Yorha_Pdf.gif" alt="YoRHa OS Önizleme" width="80%">
</p>

> **Not:** Giften kaynaklı çözünürlük berbat ve hayır gif donmadı bi kaç saniye boşluk var. Optimizasyon baby... 

---

# Instagram Çevrimdışı Klonlayıcı & Yedekleyici 📸
*API limitlerine son. Tamamen yerel, tamamen senin.*

Instagram API'sinin kısıtlamalarına (429 Limit Hataları) takılmadan, doğrudan kendi Firefox oturumunuz üzerinden çalışan "hayalet" bir yedekleme aracıdır. Sadece fotoğrafları indirmekle kalmaz, hedef profilin **internetsiz çalışan, etkileşimli bir HTML kopyasını** oluşturur!

### 🌟 Öne Çıkan Özellikler:
*   **🚀 Limitsiz & Şifresiz (Anti-Ban):** Resmi API veya arka kapılar kullanmaz. Selenium ile doğrudan sizin Firefox profilinizi (çerezlerinizi) kullanarak sayfayı bir insan gibi gezer. Şifre girmenize gerek yoktur ve ban riski sıfırdır.
*   **🧠 Akıllı "Ctrl+A" Veri Çekici:** Instagram'ın sürekli değişen karmaşık HTML yapısını atlatmak için sayfanın düz metnini okur. Biyografi, gönderi, takipçi ve takip sayılarını sıfır hatayla ayıklar.
*   **🎞️ Tam Kapsamlı Medya Desteği:** Tekli fotoğraflar, videolar (MP4), kaydırmalı (Carousel) gönderiler ve yüksek çözünürlüklü Profil Fotoğrafını (PP) eksiksiz indirir.
*   **✨ Özel Kapaklı Öne Çıkanlar (Highlights):** Profildeki öne çıkan hikayeleri sadece içindeki videolarla değil, özel kapak fotoğrafları ve isimleriyle birlikte gruplayarak arşivler.
*   **🌐 İnteraktif Yerel Galeri (Dark Mode):** İndirilen tüm verilerle şık, karanlık temalı bir `index.html` inşa eder. Tıklanabilir postlar, tam ekran medya görüntüleyici (Modal/Lightbox) ve klavye ok tuşlarıyla kaydırma desteği ile **gerçek Instagram deneyimini çevrimdışı sunar.**
*   **📦 Otomatik Paketleme:** İşlem bittiğinde hiçbir ortalığı dağıtmaz; tüm arşivi `Instagram_Yedekleri` klasörü altında düzenli bir `.zip` dosyası haline getirir.

## 🎥 Sistem Önizlemesi
*(Aşağıdaki videoyu oynatarak arayüzü ve işlemleri inceleyebilirsiniz)*

<p align="center">
  <img src="Pdf/Yorha_Pdf.gif" alt="YoRHa OS Önizleme" width="80%">
</p>

> **Not:** Giften kaynaklı çözünürlük berbat ve hayır gif donmadı bi kaç saniye boşluk var. Optimizasyon baby... 

---

## ⚙️ Temel İşlevler

Bu araç, PDF dosyaları üzerinde ihtiyaç duyulan tüm temel yapısal modifikasyonları destekler:

*   **📄 Çoklu PDF Birleştirme:** Listeye eklenen veya sürüklenen birden fazla PDF dosyasının, sadece sizin belirlediğiniz sayfa aralıklarını tek bir belgede birleştirir.
*   **✂️ Özel Sayfa Ayırma (Extract):** Büyük bir PDF dosyasının içinden sadece istediğiniz sayfaları (Örn: 1-5, 8, 12) kopararak yeni bir dosya olarak kaydeder.
*   **🗂️ Tek Tek Sayfalara Bölme (Split):** Seçilen belgeyi tamamen parçalayarak, her bir sayfasını belirlediğiniz klasöre ayrı ayrı PDF'ler olarak dağıtır.
*   **👁️ Yüksek Çözünürlüklü Önizleme:** PyMuPDF motoru sayesinde PDF sayfaları render edilir ve DPI destekli ekranda keskin bir şekilde önizlenir. Sadece işleme dahil edilecek sayfalar gösterilir.
*   **🖱️ Sürükle-Bırak (Drag & Drop):** Dosyalarınızı Windows gezgininden doğrudan uygulamanın içerisine fırlatarak anında işlem sırasına alabilirsiniz.
*   **✨ Özel Tasarım UI:** Açılış animasyonu (Splash Screen), DPI duyarlı (bulanıklaşmayan) keskin arayüz, özel renk paleti, dantel (lace) overlay'i ve Windows 11 API entegrasyonu ile boyanmış başlık çubuğu.

---

## 🛠️ Kullanılan Kütüphaneler ve Teknolojiler

Projenin altyapısında hızlı render almak ve modern bir masaüstü deneyimi sunmak için aşağıdaki kütüphaneler kullanılmıştır:

*   **[Python 3.x]** - Temel geliştirme dili.
*   **[Tkinter]** - Çekirdek masaüstü GUI kütüphanesi.
*   **[PyMuPDF (fitz)]** - Hızlı PDF okuma, manipülasyon (birleştirme/bölme) ve yüksek kaliteli sayfa renderlama (Pixmap) motoru.
*   **[Pillow (PIL)]** - Arayüzdeki görsellerin (Dantel motifi, varsayılan ekran ve önizleme resimleri) yeniden boyutlandırılması ve yönetimi.
*   **[tkinterdnd2]** - İşletim sistemi seviyesindeki sürükle-bırak (Drag & Drop) fonksiyonlarını Tkinter'a bağlayan altyapı.
*   **[ctypes]** - Yüksek DPI keskinliğini zorlamak ve Windows başlık çubuğu (DWM) rengini değiştirmek için işletim sistemi API bağlantıları.

---


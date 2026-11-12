


# Otomotiv Boyahanesinde Q-Öğrenme ile Dinamik Araç Sıralama Optimizasyonu

Bu proje, otomotiv üretim bantlarındaki boyahane istasyonlarında yaşanan hat yıkama (purging) maliyetlerini en aza indirmek için geliştirilmiş bir Pekiştirmeli Öğrenme (Reinforcement Learning) ve simülasyon çalışmasıdır. Dinamik araç sıralaması problemi, Q-Learning algoritması ile çözülmüş ve elde edilen optimal politika (policy), Unity oyun motoru üzerinde simüle edilmiştir.

## 🎯 Problem Tanımı
Otomotiv boyahanelerinde peş peşe farklı renkte araçlar boyandığında, boya tabancalarının ve hatların temizlenmesi (purging) gerekir. Bu işlem;
* Solvent israfına,
* Zaman kaybına,
* Operasyonel maliyetlerin artmasına neden olur.

Özellikle zıt renkler arası geçişler maksimum temizlik gerektirir. Projenin temel amacı, belirli bir sipariş kotası (Örn: 23 Siyah, 14 Gri, 9 Beyaz) bulunan araçların hatta giriş sırasını, renk değişim maliyetlerini minimize edecek şekilde dinamik olarak planlayan otonom bir ajan geliştirmektir.

## 🧠 Pekiştirmeli Öğrenme Mimarisi
Ajanın eğitimi için özel bir `PaintShopEnv` ortamı inşa edilmiştir. Model, durum-eylem (state-action) uzayını keşfederek en yüksek ödülü getiren dizilimi öğrenir.

### 📊 Durum (State) Uzayı
Durum uzayı 4 temel parametreden oluşur:
* **Mevcut Renk:** O an boya tabancasında bulunan renk *(0: Başlangıç, 1: Siyah, 2: Gri, 3: Beyaz)*
* **Kalan Siyah Araç Siparişi**
* **Kalan Gri Araç Siparişi**
* **Kalan Beyaz Araç Siparişi**

### ⚙️ Eylem (Action) Uzayı
Ajan, sıradaki aracı boyamak için 3 farklı eylemden birini seçebilir:
1. **Siyaha boya**
2. **Griye boya**
3. **Beyaza boya**

### ⚖️ Ödül ve Ceza Mekanizması (Reward Function)
Sistem, maliyetli temizlik işlemlerini sert cezalarla engellerken, aynı renk boyama işlemlerini ödüllendirir:

* **Boş ➔ Herhangi (+1):** Başlangıçta ilk aracın boyanması.
* **Aynı Renk ➔ Aynı Renk (+1):** Renk değişimi yok, temizlik maliyeti sıfır.
* **Siyah ➔ Beyaz (-100):** En yüksek purging maliyeti. Tam hat temizliği gerektirir.
* **Beyaz ➔ Siyah (-75):** Yüksek purging maliyeti.
* **Diğer Renk Değişimleri (-50):** Kısmi temizlik gerektiren geçişler (Örn: Siyah ➔ Gri).
* **Kritik Hata / Ölümcül (-100):** Kotası bitmiş bir rengin tekrar seçilmesi.

### 🎛️ Eğitim Hiperparametreleri
Eğitim, Epsilon-Greedy stratejisi kullanılarak **10.000 bölüm (episode)** boyunca gerçekleştirilir.

* **Öğrenme Oranı (Alpha - α):** 0.1
* **İndirim Faktörü (Gamma - γ):** 0.9
* **Keşif Oranı (Epsilon - ϵ):** 0.9

Eğitim tamamlandıktan sonra elde edilen matris, Unity simülasyonunda kullanılmak üzere `QTable.json` formatında dışa aktarılır.

## 🎮 3D Simülasyon - Unity C#
Eğitilen ajanın kararları, Unity üzerinde geliştirilen `PaintShopController` ve `CarBehavior` sınıfları aracılığıyla görselleştirilir. Bu sistem, ajanın beyni olan Q-Tablosunu okuyarak üretim bandını otonom şekilde yönetir.

### 🚀 Çalışma Prensibi
* **Veri Entegrasyonu:** Oyun başladığında `QTable.json` dosyası `Newtonsoft.Json` kütüphanesi ile belleğe alınır.
* **Dinamik Karar Alma:** Kalan araç kotalarına göre sistemin anlık durum (State) string'i oluşturulur (Örn: `1,23,14,9`). Bu duruma karşılık gelen en yüksek Q değerine sahip eylem tablodan çekilir.
* **Safety Lock (Güvenlik Kilidi):** Üretim bandında bir anomali yaşanmaması için, Q-Tablosunun nadir durumlarda kotası bitmiş bir rengi önermesi ihtimaline karşı `targetColor` mantıksal bir kilit ile devreye girerek ajanı mevcut renklere yönlendirir.
* **Araç Yönlendirme:** Araç, robot kolu (`robotArm`) pozisyonuna gelip boyanır ve kendi renk grubunun şeridine yönlendirilip bandı terk eder.
### 🚀 Simülasyon Kısmı

<img width="823" height="527" alt="Ekran Resmi 2026-11-12 15 18 04" src="https://github.com/user-attachments/assets/ce08c6ac-058e-4a21-9307-03da5a833291" />
<img width="823" height="527" alt="Ekran Resmi 2026-11-12 15 15 57" src="https://github.com/user-attachments/assets/f9898ed6-50bf-499e-9a45-8949602a2d16" />

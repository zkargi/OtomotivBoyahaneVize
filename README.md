 # Otomotiv Boyahanesinde Q-Öğrenme ile Dinamik Araç Sıralama Optimizasyonu

Bu proje, otomotiv üretim bantlarındaki boyahane istasyonlarında yaşanan hat yıkama (purging) maliyetlerini en aza indirmek için geliştirilmiş bir **Pekiştirmeli Öğrenme (Reinforcement Learning)** ve simülasyon çalışmasıdır. Dinamik araç sıralaması problemi, **Q-Learning** algoritması ile çözülmüş ve elde edilen optimal politika (policy), **Unity oyun motoru** üzerinde simüle edilmiştir.

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
1. **Siyah (1)**
2. **Gri (2)**
3. **Beyaz (3)**

### ⚖️ Ödül ve Ceza Mekanizması (Reward Function)
Sistem, maliyetli temizlik işlemlerini sert cezalarla engellerken, aynı renk boyama işlemlerini ödüllendirir:
* *(Görselde metin burada kesildiği için buraya eylem başı ödül/ceza puanlarınızı liste olarak ekleyebilirsiniz. Örn: "Aynı renge devam: +10 puan, Farklı renge geçiş: -50 puan")*

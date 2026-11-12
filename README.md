 # Otomotiv Boyahanesinde Q-Öğrenme ile Dinamik Araç Sıralama Optimizasyonu

Bu proje, otomotiv üretim bantlarındaki boyahane istasyonlarında yaşanan hat yıkama (purging) maliyetlerini en aza indirmek için geliştirilmiş bir **Pekiştirmeli Öğrenme (Reinforcement Learning)** ve simülasyon çalışmasıdır[cite: 1]. Dinamik araç sıralaması problemi, **Q-Learning** algoritması ile çözülmüş ve elde edilen optimal politika (policy), **Unity oyun motoru** üzerinde simüle edilmiştir[cite: 1].

## 🎯 Problem Tanımı

Otomotiv boyahanelerinde peş peşe farklı renkte araçlar boyandığında, boya tabancalarının ve hatların temizlenmesi (purging) gerekir[cite: 1]. Bu işlem;
* Solvent israfına,
* Zaman kaybına,
* Operasyonel maliyetlerin artmasına neden olur[cite: 1].

Özellikle zıt renkler arası geçişler maksimum temizlik gerektirir[cite: 1]. Projenin temel amacı, belirli bir sipariş kotası (Örn: 23 Siyah, 14 Gri, 9 Beyaz) bulunan araçların hatta giriş sırasını, renk değişim maliyetlerini minimize edecek şekilde dinamik olarak planlayan otonom bir ajan geliştirmektir[cite: 1].

## 🧠 Pekiştirmeli Öğrenme Mimarisi

Ajanın eğitimi için özel bir `PaintShopEnv` ortamı inşa edilmiştir[cite: 1]. Model, durum-eylem (state-action) uzayını keşfederek en yüksek ödülü getiren dizilimi öğrenir[cite: 1].

### 📊 Durum (State) Uzayı
Durum uzayı 4 temel parametreden oluşur[cite: 1]:
* **Mevcut Renk:** O an boya tabancasında bulunan renk *(0: Başlangıç, 1: Siyah, 2: Gri, 3: Beyaz)*[cite: 1].
* **Kalan Siyah Araç Siparişi**[cite: 1]
* **Kalan Gri Araç Siparişi**[cite: 1]
* **Kalan Beyaz Araç Siparişi**[cite: 1]

### ⚙️ Eylem (Action) Uzayı
Ajan, sıradaki aracı boyamak için 3 farklı eylemden birini seçebilir[cite: 1]:
1. **Siyah (1)**[cite: 1]
2. **Gri (2)**[cite: 1]
3. **Beyaz (3)**[cite: 1]

### ⚖️ Ödül ve Ceza Mekanizması (Reward Function)
Sistem, maliyetli temizlik işlemlerini sert cezalarla engellerken, aynı renk boyama işlemlerini ödüllendirir[cite: 1]:
* *(Görselde metin burada kesildiği için buraya eylem başı ödül/ceza puanlarınızı liste olarak ekleyebilirsiniz. Örn: "Aynı renge devam: +10 puan, Farklı renge geçiş: -50 puan")*

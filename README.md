# DXF Görüntüleyici

Bu proje, DXF dosyalarını görüntülemek için Python ve PyQt6 kullanılarak geliştirilmiş bir uygulamadır.

## Teknolojiler

- Python 3.x
- PyQt6
- ezdxf

## Gereksinimler
```
pip install PyQt6
pip install ezdxf
```

## Kullanım
```
python src/main.py
```

## Özellikler

### Mevcut Özellikler

- DXF dosyalarını yükleme ve görüntüleme
- Desteklenen DXF varlıkları:
  - Çizgi (LINE)
  - Daire (CIRCLE)
  - Yay (ARC)
  - Çoklu çizgi (LWPOLYLINE)
  - Çokgen (POLYLINE)
- Görüntüleme özellikleri:
  - Yakınlaştırma/Uzaklaştırma (fare tekerleği ile)
  - Kaydırma (sol fare tuşu ile sürükleme)
  - Otomatik merkeze hizalama
  - Antialiasing desteği
- Katman yönetimi:
  - Katmanları gösterme/gizleme
- Çizim özellikleri:
  - Varlık renklerini destekleme
  - Çizgi tiplerini destekleme (CONTINUOUS, DASHED, DOTTED, DASHDOT)

### Yapılacaklar

- [ ] Daha fazla DXF varlık desteği (TEXT, MTEXT, DIMENSION vb.)
- [ ] Ölçeklendirme göstergesi
- [ ] Seçim aracı
- [ ] Ölçüm araçları
- [ ] DXF dosyası özellikleri görüntüleme
- [ ] Katman listesi arayüzü
- [ ] Yazdırma desteği
- [ ] Farklı formatlara dışa aktarma (PNG, PDF vb.)
- [ ] Çoklu dosya desteği (sekmeler)
- [ ] Geri alma/yineleme işlemleri
- [ ] Performans optimizasyonları


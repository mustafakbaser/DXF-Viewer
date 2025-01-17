# DXF Görüntüleyici

Modern bir DXF dosya görüntüleyici ve düzenleyici uygulaması.

## Teknolojiler

- Python 3.x
- PyQt6
- ezdxf
- numpy
- matplotlib

## Gereksinimler
```bash
pip install -r requirements.txt
```

## Kullanım
```bash
python src/main.py
```

## Özellikler

### Görüntüleme ve Gezinme
- DXF dosyalarını yükleme ve görüntüleme
- Yakınlaştırma/Uzaklaştırma (fare tekerleği)
- Kaydırma (sol fare tuşu ile sürükleme)
- Otomatik merkeze hizalama
- Antialiasing desteği

### Katman Yönetimi
- Katmanları gösterme/gizleme
- Tüm katmanları seçme/temizleme
- Katmanlar arası gezinme (önceki/sonraki)
- Katman renk desteği (ACI ve RGB)

### Seçim ve Düzenleme
- CTRL + Sol tık ile seçim alanı oluşturma
- Çoklu nesne seçimi (CTRL tuşu ile)
- Seçili nesneleri vurgulama
- Nesne özelliklerini düzenleme

### Desteklenen DXF Varlıkları
- Çizgi (LINE)
- Daire (CIRCLE)
- Yay (ARC)
- Çoklu çizgi (LWPOLYLINE)
- Çokgen (POLYLINE)
- Spline (SPLINE)
- Elips (ELLIPSE)
- Nokta (POINT)
- Metin (TEXT)

### Arayüz Özellikleri
- Modern ve kullanıcı dostu tasarım
- Dosya bilgileri görüntüleme
- Katman ağacı görünümü
- Özelleştirilmiş araç çubuğu

## Proje Yapısı
```
src/
├── main.py           # Ana uygulama başlangıç noktası
├── viewer.py         # Ana pencere ve uygulama mantığı
├── dxf_handler.py    # DXF dosya işlemleri
└── widgets/
    ├── canvas.py     # Çizim alanı
    └── file_panel.py # Dosya ve katman yönetimi paneli
```	

## Yapılacaklar

- [ ] Daha fazla DXF varlık desteği (MTEXT, DIMENSION)
- [ ] Ölçeklendirme göstergesi
- [ ] Ölçüm araçları
- [ ] Yazdırma desteği
- [ ] Farklı formatlara dışa aktarma (PNG, PDF)
- [ ] Çoklu dosya desteği (sekmeler)
- [ ] Geri alma/yineleme işlemleri
- [ ] Performans optimizasyonları


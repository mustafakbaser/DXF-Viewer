"""
Translation module for DXF Viewer application.
Contains all text strings in different languages.
"""

class Translations:
    # Available languages
    ENGLISH = "en"
    TURKISH = "tr"
    
    # Default language
    DEFAULT_LANGUAGE = ENGLISH
    
    # All translations
    STRINGS = {
        # Main window
        "app_title": {
            ENGLISH: "DXF Viewer",
            TURKISH: "DXF Görüntüleyici"
        },
        "ready_status": {
            ENGLISH: "Ready",
            TURKISH: "Hazır"
        },
        
        # Menu items
        "menu_file": {
            ENGLISH: "File",
            TURKISH: "Dosya"
        },
        "menu_open": {
            ENGLISH: "Open",
            TURKISH: "Aç"
        },
        "menu_save": {
            ENGLISH: "Save",
            TURKISH: "Kaydet"
        },
        "menu_exit": {
            ENGLISH: "Exit",
            TURKISH: "Çıkış"
        },
        "menu_language": {
            ENGLISH: "Language",
            TURKISH: "Dil"
        },
        "menu_english": {
            ENGLISH: "English",
            TURKISH: "İngilizce"
        },
        "menu_turkish": {
            ENGLISH: "Turkish",
            TURKISH: "Türkçe"
        },
        "menu_about": {
            ENGLISH: "About",
            TURKISH: "Hakkında"
        },
        "menu_about_app": {
            ENGLISH: "About DXF Viewer",
            TURKISH: "DXF Görüntüleyici Hakkında"
        },
        
        # File panel
        "open_file": {
            ENGLISH: "Open File",
            TURKISH: "Dosya Aç"
        },
        "select_all": {
            ENGLISH: "Select All",
            TURKISH: "Tümünü Seç"
        },
        "clear_all": {
            ENGLISH: "Clear All",
            TURKISH: "Temizle"
        },
        "layers": {
            ENGLISH: "Layers",
            TURKISH: "Katmanlar"
        },
        "prev": {
            ENGLISH: "Prev",
            TURKISH: "Önceki"
        },
        "fill": {
            ENGLISH: "Fill",
            TURKISH: "Dolgu"
        },
        "next": {
            ENGLISH: "Next",
            TURKISH: "Sonraki"
        },
        
        # Tooltips
        "tooltip_open_file": {
            ENGLISH: "Open a DXF file",
            TURKISH: "Bir DXF dosyası aç"
        },
        "tooltip_select_all": {
            ENGLISH: "Show all layers",
            TURKISH: "Tüm katmanları görünür yap"
        },
        "tooltip_clear_all": {
            ENGLISH: "Hide all layers",
            TURKISH: "Tüm katmanları gizle"
        },
        "tooltip_prev": {
            ENGLISH: "Show previous layer",
            TURKISH: "Önceki katmanı göster"
        },
        "tooltip_fill": {
            ENGLISH: "Toggle layer fill mode",
            TURKISH: "Katmanları doldur/boşalt"
        },
        "tooltip_next": {
            ENGLISH: "Show next layer",
            TURKISH: "Sonraki katmanı göster"
        },
        
        # File dialog
        "select_dxf_file": {
            ENGLISH: "Select DXF File",
            TURKISH: "DXF Dosyası Seç"
        },
        "dxf_files": {
            ENGLISH: "DXF Files (*.dxf)",
            TURKISH: "DXF Dosyaları (*.dxf)"
        },
        
        # Info display
        "file": {
            ENGLISH: "File",
            TURKISH: "Dosya"
        },
        "layer_count": {
            ENGLISH: "Layer Count",
            TURKISH: "Katman Sayısı"
        },
        "geometry_types": {
            ENGLISH: "Geometry Types",
            TURKISH: "Geometri Türleri"
        },
        
        # Canvas context menu
        "edit_properties": {
            ENGLISH: "Edit Properties",
            TURKISH: "Özellikleri Düzenle"
        },
        "delete": {
            ENGLISH: "Delete",
            TURKISH: "Sil"
        },
        "clear_selection": {
            ENGLISH: "Clear Selection",
            TURKISH: "Seçimi Temizle"
        },
        
        # Entity properties dialog
        "entity_properties": {
            ENGLISH: "Entity Properties",
            TURKISH: "Nesne Özellikleri"
        },
        "type": {
            ENGLISH: "Type",
            TURKISH: "Tür"
        },
        "layer": {
            ENGLISH: "Layer",
            TURKISH: "Katman"
        },
        "color": {
            ENGLISH: "Color",
            TURKISH: "Renk"
        },
        "select_color": {
            ENGLISH: "Select Color",
            TURKISH: "Renk Seç"
        },
        "start_x": {
            ENGLISH: "Start X",
            TURKISH: "Başlangıç X"
        },
        "start_y": {
            ENGLISH: "Start Y",
            TURKISH: "Başlangıç Y"
        },
        "end_x": {
            ENGLISH: "End X",
            TURKISH: "Bitiş X"
        },
        "end_y": {
            ENGLISH: "End Y",
            TURKISH: "Bitiş Y"
        },
        "center_x": {
            ENGLISH: "Center X",
            TURKISH: "Merkez X"
        },
        "center_y": {
            ENGLISH: "Center Y",
            TURKISH: "Merkez Y"
        },
        "radius": {
            ENGLISH: "Radius",
            TURKISH: "Yarıçap"
        },
        "start_angle": {
            ENGLISH: "Start Angle",
            TURKISH: "Başlangıç Açısı"
        },
        "end_angle": {
            ENGLISH: "End Angle",
            TURKISH: "Bitiş Açısı"
        },
        
        # Error messages
        "error": {
            ENGLISH: "Error",
            TURKISH: "Hata"
        },
        "dxf_loading_error": {
            ENGLISH: "DXF loading error",
            TURKISH: "DXF yükleme hatası"
        },
        "color_conversion_error": {
            ENGLISH: "Color conversion error",
            TURKISH: "Renk dönüşüm hatası"
        },
        "spline_bounds_error": {
            ENGLISH: "Spline bounds calculation error",
            TURKISH: "Spline sınırları hesaplama hatası"
        },
        "polyline_drawing_error": {
            ENGLISH: "Polyline drawing error",
            TURKISH: "Polyline çizim hatası"
        },
        "spline_drawing_error": {
            ENGLISH: "Spline drawing error",
            TURKISH: "Spline çizim hatası"
        },
        
        # About dialog
        "about_title": {
            ENGLISH: "About DXF Viewer",
            TURKISH: "DXF Görüntüleyici Hakkında"
        },
        "about_text": {
            ENGLISH: """
<h1>DXF Viewer</h1>
<p>A modern DXF file viewer and editor application with a clean, professional interface.</p>
<p>Developed by Mustafa Kürşad BAŞER</p>
<p>© 2025 All rights reserved.</p>
""",
            TURKISH: """
<h1>DXF Görüntüleyici</h1>
<p>Modern bir DXF dosya görüntüleyici ve düzenleyici uygulaması.</p>
<p>Mustafa Kürşad BAŞER tarafından geliştirildi.</p>
<p>© 2025 Tüm hakları saklıdır.</p>
"""
        },
    }
    
    @staticmethod
    def get(key, language=DEFAULT_LANGUAGE):
        """Get translation for a key in the specified language"""
        if key not in Translations.STRINGS:
            return key
        
        translations = Translations.STRINGS[key]
        if language not in translations:
            return translations[Translations.DEFAULT_LANGUAGE]
        
        return translations[language] 
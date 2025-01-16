from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                           QLabel, QFileDialog, QTextEdit, QTreeWidget,
                           QTreeWidgetItem, QCheckBox, QHBoxLayout, QToolBar, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QIcon, QAction
from dxf_handler import DXFHandler

class LayerItem(QTreeWidgetItem):
    def __init__(self, layer_name, color):
        super().__init__([layer_name])
        self.layer_name = layer_name
        self.color = color
        self.setCheckState(0, Qt.CheckState.Checked)

class FilePanel(QWidget):
    file_loaded = pyqtSignal(str)
    layer_visibility_changed = pyqtSignal(str, bool)  # layer_name, is_visible
    
    def __init__(self):
        super().__init__()
        self.dxf_handler = DXFHandler()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Dosya seçme butonu
        self.select_btn = QPushButton("Dosya Seç")
        self.select_btn.clicked.connect(self._select_file)
        layout.addWidget(self.select_btn)
        
        # Katman kontrol butonları için horizontal layout
        control_layout = QHBoxLayout()
        
        # Tümünü Seç butonu
        self.select_all_btn = QPushButton("Tümünü Seç")
        self.select_all_btn.setToolTip("Tüm katmanları görünür yap")
        self.select_all_btn.clicked.connect(self._select_all_layers)
        control_layout.addWidget(self.select_all_btn)
        
        # Temizle butonu
        self.clear_all_btn = QPushButton("Temizle")
        self.clear_all_btn.setToolTip("Tüm katmanları gizle")
        self.clear_all_btn.clicked.connect(self._clear_all_layers)
        control_layout.addWidget(self.clear_all_btn)
        
        # Kontrol butonlarını layout'a ekle
        layout.addLayout(control_layout)
        
        # Katman ağacı başlığı
        layer_tree_label = QLabel("Katmanlar")
        layout.addWidget(layer_tree_label)
        
        # Katman ağacı
        self.layer_tree = QTreeWidget()
        self.layer_tree.setHeaderLabel("Katmanlar")
        self.layer_tree.itemChanged.connect(self._on_layer_visibility_changed)
        layout.addWidget(self.layer_tree)
        
        # Gezinme butonları için horizontal layout
        nav_layout = QHBoxLayout()
        
        # Önceki Katman butonu
        self.prev_layer_btn = QPushButton("← Önceki")
        self.prev_layer_btn.setToolTip("Önceki katmanı göster")
        self.prev_layer_btn.clicked.connect(self._select_previous_layer)
        nav_layout.addWidget(self.prev_layer_btn)
        
        # Sonraki Katman butonu
        self.next_layer_btn = QPushButton("Sonraki →")
        self.next_layer_btn.setToolTip("Sonraki katmanı göster")
        self.next_layer_btn.clicked.connect(self._select_next_layer)
        nav_layout.addWidget(self.next_layer_btn)
        
        # Gezinme butonlarını layout'a ekle
        layout.addLayout(nav_layout)
        
        # Dosya bilgileri
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        layout.addWidget(self.info_display)
        
        # Başlangıçta butonları devre dışı bırak
        self._update_button_states(False)
        
        # Buton stilleri için ortak stil tanımı
        button_style = """
            QPushButton {
                padding: 5px 15px;
                background: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
            QPushButton:disabled {
                color: #999;
            }
        """
        
        # Stilleri uygula
        self.select_btn.setStyleSheet(button_style)
        self.select_all_btn.setStyleSheet(button_style)
        self.clear_all_btn.setStyleSheet(button_style)
        self.prev_layer_btn.setStyleSheet(button_style)
        self.next_layer_btn.setStyleSheet(button_style)
    
    def _update_button_states(self, enabled=True):
        """Butonların aktif/pasif durumunu güncelle"""
        self.select_all_btn.setEnabled(enabled)
        self.clear_all_btn.setEnabled(enabled)
        self.prev_layer_btn.setEnabled(enabled)
        self.next_layer_btn.setEnabled(enabled)
    
    def _select_all_layers(self):
        """Tüm katmanları seçili duruma getir"""
        root = self.layer_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, Qt.CheckState.Checked)
    
    def _clear_all_layers(self):
        """Tüm katmanların seçimini kaldır"""
        root = self.layer_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, Qt.CheckState.Unchecked)
    
    def _select_previous_layer(self):
        """Önceki katmanı seç"""
        current_item = self.layer_tree.currentItem()
        if not current_item:
            return
            
        current_index = self.layer_tree.indexOfTopLevelItem(current_item)
        if current_index > 0:
            prev_item = self.layer_tree.topLevelItem(current_index - 1)
            self.layer_tree.setCurrentItem(prev_item)
            prev_item.setCheckState(0, Qt.CheckState.Checked)
            current_item.setCheckState(0, Qt.CheckState.Unchecked)
    
    def _select_next_layer(self):
        """Sonraki katmanı seç"""
        current_item = self.layer_tree.currentItem()
        if not current_item:
            return
            
        current_index = self.layer_tree.indexOfTopLevelItem(current_item)
        if current_index < self.layer_tree.topLevelItemCount() - 1:
            next_item = self.layer_tree.topLevelItem(current_index + 1)
            self.layer_tree.setCurrentItem(next_item)
            next_item.setCheckState(0, Qt.CheckState.Checked)
            current_item.setCheckState(0, Qt.CheckState.Unchecked)
    
    def _select_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "DXF Dosyası Seç", "", "DXF Dosyaları (*.dxf)"
        )
        if filepath:
            try:
                info = self.dxf_handler.load_file(filepath)
                self._update_info_display(info)
                self._update_layer_tree()
                self.file_loaded.emit(filepath)
            except Exception as e:
                self.info_display.setText(f"Hata: {str(e)}")
    
    def _update_layer_tree(self):
        self.layer_tree.clear()
        if not self.dxf_handler.doc:
            self._update_button_states(False)
            return
            
        for layer in self.dxf_handler.doc.layers:
            color = self._get_layer_color(layer)
            item = LayerItem(layer.dxf.name, color)
            self.layer_tree.addTopLevelItem(item)
        
        # Katmanlar yüklendiğinde butonları aktif et
        self._update_button_states(True)
        
        # İlk katmanı seç
        if self.layer_tree.topLevelItemCount() > 0:
            first_item = self.layer_tree.topLevelItem(0)
            self.layer_tree.setCurrentItem(first_item)
    
    def _get_layer_color(self, layer):
        try:
            # Önce RGB değerini kontrol et
            if layer.rgb is not None:
                return QColor(*layer.rgb)
            
            # ACI rengi kontrol et
            if hasattr(layer.dxf, 'color'):
                color_index = layer.dxf.color
                if color_index >= 0:
                    return self._aci_to_rgb(color_index)
        except Exception as e:
            print(f"Katman rengi dönüşüm hatası: {str(e)}")
        
        return QColor(255, 255, 255)  # Varsayılan beyaz
    
    def _aci_to_rgb(self, color_index):
        """AutoCAD Color Index (ACI) rengini RGB'ye çevirir"""
        # AutoCAD standart renk tablosu
        aci_colors = {
            0: (255, 255, 255),   # ByBlock (Beyaz)
            1: (255, 0, 0),       # Kırmızı
            2: (255, 255, 0),     # Sarı
            3: (0, 255, 0),       # Yeşil
            4: (0, 255, 255),     # Cyan
            5: (0, 0, 255),       # Mavi
            6: (255, 0, 255),     # Magenta
            7: (255, 255, 255),   # Beyaz
            8: (128, 128, 128),   # Koyu Gri
            9: (192, 192, 192),   # Açık Gri
            256: (255, 255, 255), # ByLayer (Beyaz)
        }
        
        return QColor(*aci_colors.get(color_index, (255, 255, 255)))
    
    def _on_layer_visibility_changed(self, item, column):
        if isinstance(item, LayerItem):
            is_visible = item.checkState(0) == Qt.CheckState.Checked
            self.layer_visibility_changed.emit(item.layer_name, is_visible)
    
    def _update_info_display(self, info):
        text = f"Dosya: {info.filename}\n"
        text += f"Katman Sayısı: {info.layer_count}\n\n"
        text += "Geometri Türleri:\n"
        for entity_type, count in info.entity_counts.items():
            text += f"- {entity_type}: {count}\n"
        self.info_display.setText(text) 
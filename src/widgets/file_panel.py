from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                           QLabel, QFileDialog, QTextEdit, QTreeWidget,
                           QTreeWidgetItem, QCheckBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
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
        
        # Katman ağacı
        self.layer_tree = QTreeWidget()
        self.layer_tree.setHeaderLabel("Katmanlar")
        self.layer_tree.itemChanged.connect(self._on_layer_visibility_changed)
        layout.addWidget(self.layer_tree)
        
        # Dosya bilgileri
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        layout.addWidget(self.info_display)
    
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
            return
            
        for layer in self.dxf_handler.doc.layers:
            color = self._get_layer_color(layer)
            item = LayerItem(layer.dxf.name, color)
            self.layer_tree.addTopLevelItem(item)
    
    def _get_layer_color(self, layer):
        # ACI (AutoCAD Color Index) rengini RGB'ye dönüştür
        try:
            rgb = layer.rgb
            if rgb is None:  # Eğer RGB tanımlanmamışsa
                return QColor(0, 0, 0)  # Varsayılan siyah
            return QColor(*rgb)
        except:
            return QColor(0, 0, 0)
    
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
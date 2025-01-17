from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QWidget
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from widgets.file_panel import FilePanel
from widgets.canvas import DXFCanvas

class DXFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DXF Görüntüleyici")
        self.setGeometry(100, 100, 1200, 800)
        
        # Aydınlık mod için palette ayarları
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QTreeWidget {
                border: 1px solid #c0c0c0;
            }
            QTextEdit {
                border: 1px solid #c0c0c0;
            }
        """)
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Sol panel (2/8)
        self.file_panel = FilePanel()
        layout.addWidget(self.file_panel, stretch=2)
        
        # Sağ panel - Canvas (6/8)
        self.canvas = DXFCanvas()
        layout.addWidget(self.canvas, stretch=6)
        
        # Sinyal bağlantıları
        self.file_panel.file_loaded.connect(self.canvas.load_dxf)
        self.file_panel.layer_visibility_changed.connect(
            self.canvas.set_layer_visibility
        )
        
        # Canvas referansını FilePanel'e ekle
        self.file_panel.canvas = self.canvas 
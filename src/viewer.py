from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QStatusBar
from PyQt6.QtGui import QPalette, QColor, QIcon
from PyQt6.QtCore import Qt
from widgets.file_panel import FilePanel
from widgets.canvas import DXFCanvas

class DXFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DXF Viewer")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("icon.ico"))
        
        # Set fullscreen on startup
        self.showMaximized()
        
        # Modern light theme palette settings
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                background-color: white;
                color: #2c3e50;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QTreeWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
            }
            QTreeWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QTreeWidget::item:hover {
                background-color: #ecf0f1;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f5f5f5;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc3c7;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95a5a6;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QStatusBar {
                background-color: #f8f9fa;
                color: #2c3e50;
                border-top: 1px solid #bdc3c7;
                padding: 5px;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Left panel (1/7 of the width)
        self.file_panel = FilePanel()
        layout.addWidget(self.file_panel, stretch=1)
        
        # Right panel - Canvas (6/7 of the width)
        self.canvas = DXFCanvas()
        layout.addWidget(self.canvas, stretch=6)
        
        # Signal connections
        self.file_panel.file_loaded.connect(self.canvas.load_dxf)
        self.file_panel.layer_visibility_changed.connect(
            self.canvas.set_layer_visibility
        )
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Canvas reference to FilePanel
        self.file_panel.canvas = self.canvas 
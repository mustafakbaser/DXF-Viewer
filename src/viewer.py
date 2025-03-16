from PyQt6.QtWidgets import (QMainWindow, QHBoxLayout, QWidget, QStatusBar, 
                           QMenuBar, QMenu, QMessageBox)
from PyQt6.QtGui import QPalette, QColor, QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSignal
from widgets.file_panel import FilePanel
from widgets.canvas import DXFCanvas
from translations import Translations
from settings import Settings

class DXFViewer(QMainWindow):
    # Signal to notify language change
    language_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Initialize settings
        self.settings = Settings()
        
        # Set current language
        self.current_language = self.settings.language
        
        self._init_ui()
        self._create_menu()
        self._connect_signals()
        
        # Set fullscreen on startup if configured
        if self.settings.get("window_state", {}).get("maximized", True):
            self.showMaximized()
    
    def _init_ui(self):
        self._update_window_title()
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("icon.ico"))
        
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
            QMenuBar {
                background-color: #f8f9fa;
                color: #2c3e50;
                border-bottom: 1px solid #bdc3c7;
            }
            QMenuBar::item {
                padding: 5px 10px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu {
                background-color: white;
                border: 1px solid #bdc3c7;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #bdc3c7;
                margin: 5px 0px;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Left panel (1/7 of the width)
        self.file_panel = FilePanel(self.current_language)
        layout.addWidget(self.file_panel, stretch=1)
        
        # Right panel - Canvas (6/7 of the width)
        self.canvas = DXFCanvas(self.current_language)
        layout.addWidget(self.canvas, stretch=6)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()
        
        # Canvas reference to FilePanel
        self.file_panel.canvas = self.canvas
    
    def _create_menu(self):
        # Create menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu(self._tr("menu_file"))
        
        # Open action
        open_action = QAction(QIcon.fromTheme("document-open"), self._tr("menu_open"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.file_panel._select_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction(QIcon.fromTheme("application-exit"), self._tr("menu_exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Language menu
        language_menu = menu_bar.addMenu(self._tr("menu_language"))
        
        # English action
        english_action = QAction(self._tr("menu_english"), self)
        english_action.setCheckable(True)
        english_action.setChecked(self.current_language == Translations.ENGLISH)
        english_action.triggered.connect(lambda: self._change_language(Translations.ENGLISH))
        language_menu.addAction(english_action)
        
        # Turkish action
        turkish_action = QAction(self._tr("menu_turkish"), self)
        turkish_action.setCheckable(True)
        turkish_action.setChecked(self.current_language == Translations.TURKISH)
        turkish_action.triggered.connect(lambda: self._change_language(Translations.TURKISH))
        language_menu.addAction(turkish_action)
        
        # About menu
        about_menu = menu_bar.addMenu(self._tr("menu_about"))
        
        # About action
        about_action = QAction(QIcon.fromTheme("help-about"), self._tr("menu_about_app"), self)
        about_action.triggered.connect(self._show_about_dialog)
        about_menu.addAction(about_action)
        
        # Store language actions for updating checked state
        self.language_actions = {
            Translations.ENGLISH: english_action,
            Translations.TURKISH: turkish_action
        }
    
    def _connect_signals(self):
        # Connect signals
        self.file_panel.file_loaded.connect(self.canvas.load_dxf)
        self.file_panel.layer_visibility_changed.connect(
            self.canvas.set_layer_visibility
        )
        
        # Connect language change signal
        self.language_changed.connect(self.file_panel.update_language)
        self.language_changed.connect(self.canvas.update_language)
    
    def _tr(self, key):
        """Translate text using current language"""
        return Translations.get(key, self.current_language)
    
    def _update_window_title(self):
        """Update window title with current language"""
        self.setWindowTitle(self._tr("app_title"))
    
    def _update_status_bar(self):
        """Update status bar with current language"""
        self.status_bar.showMessage(self._tr("ready_status"))
    
    def _change_language(self, language):
        """Change application language"""
        if language != self.current_language:
            self.current_language = language
            self.settings.language = language
            
            # Update UI with new language
            self._update_window_title()
            self._update_status_bar()
            
            # Update menu
            self._update_menu_language()
            
            # Notify components about language change
            self.language_changed.emit(language)
    
    def _update_menu_language(self):
        """Update menu language and checked state"""
        # Update menu bar (recreate it)
        self.menuBar().clear()
        self._create_menu()
    
    def _show_about_dialog(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            self._tr("about_title"),
            self._tr("about_text")
        ) 
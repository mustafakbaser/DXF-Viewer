from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                           QLabel, QFileDialog, QTextEdit, QTreeWidget,
                           QTreeWidgetItem, QCheckBox, QHBoxLayout, QToolBar, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QIcon, QAction, QFont
from dxf_handler import DXFHandler
from translations import Translations

class LayerItem(QTreeWidgetItem):
    def __init__(self, layer_name, color):
        super().__init__([layer_name])
        self.layer_name = layer_name
        self.color = color
        self.setCheckState(0, Qt.CheckState.Checked)

class FilePanel(QWidget):
    file_loaded = pyqtSignal(str)
    layer_visibility_changed = pyqtSignal(str, bool)  # layer_name, is_visible
    
    def __init__(self, language=Translations.DEFAULT_LANGUAGE):
        super().__init__()
        self.dxf_handler = DXFHandler()
        self.current_language = language
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Set maximum width for the panel
        self.setMaximumWidth(300)
        
        # File selection button
        self.select_btn = QPushButton(self._tr("open_file"))
        self.select_btn.setIcon(QIcon.fromTheme("document-open"))
        self.select_btn.clicked.connect(self._select_file)
        self.select_btn.setFixedHeight(32)
        self.select_btn.setToolTip(self._tr("tooltip_open_file"))
        layout.addWidget(self.select_btn)
        
        # Layer control buttons horizontal layout
        control_layout = QHBoxLayout()
        control_layout.setSpacing(4)
        
        # Select All button
        self.select_all_btn = QPushButton(self._tr("select_all"))
        self.select_all_btn.setIcon(QIcon.fromTheme("select-all"))
        self.select_all_btn.setToolTip(self._tr("tooltip_select_all"))
        self.select_all_btn.clicked.connect(self._select_all_layers)
        self.select_all_btn.setFixedWidth(140)
        self.select_all_btn.setFixedHeight(32)
        control_layout.addWidget(self.select_all_btn)
        
        # Clear All button
        self.clear_all_btn = QPushButton(self._tr("clear_all"))
        self.clear_all_btn.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_all_btn.setToolTip(self._tr("tooltip_clear_all"))
        self.clear_all_btn.clicked.connect(self._clear_all_layers)
        self.clear_all_btn.setFixedWidth(140)
        self.clear_all_btn.setFixedHeight(32)
        control_layout.addWidget(self.clear_all_btn)
        
        # Add control buttons to layout
        layout.addLayout(control_layout)
        
        # Layer tree
        self.layer_tree = QTreeWidget()
        self.layer_tree.setHeaderLabel(self._tr("layers"))
        self.layer_tree.setAnimated(True)
        self.layer_tree.itemChanged.connect(self._on_layer_visibility_changed)
        self.layer_tree.setMinimumHeight(200)
        layout.addWidget(self.layer_tree)
        
        # Navigation buttons horizontal layout
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)  # Increase spacing between buttons
        
        # Add stretch to push buttons to center
        nav_layout.addStretch(1)
        
        # Previous Layer button
        self.prev_layer_btn = QPushButton(self._tr("prev"))
        self.prev_layer_btn.setIcon(QIcon.fromTheme("go-previous"))
        self.prev_layer_btn.setToolTip(self._tr("tooltip_prev"))
        self.prev_layer_btn.clicked.connect(self._select_previous_layer)
        self.prev_layer_btn.setFixedWidth(75)
        self.prev_layer_btn.setFixedHeight(32)
        nav_layout.addWidget(self.prev_layer_btn)
        
        # Fill button
        self.fill_btn = QPushButton(self._tr("fill"))
        self.fill_btn.setIcon(QIcon.fromTheme("fill-color"))
        self.fill_btn.setToolTip(self._tr("tooltip_fill"))
        self.fill_btn.setCheckable(True)
        self.fill_btn.clicked.connect(self._toggle_fill)
        self.fill_btn.setFixedWidth(75)
        self.fill_btn.setFixedHeight(32)
        nav_layout.addWidget(self.fill_btn)
        
        # Next Layer button
        self.next_layer_btn = QPushButton(self._tr("next"))
        self.next_layer_btn.setIcon(QIcon.fromTheme("go-next"))
        self.next_layer_btn.setToolTip(self._tr("tooltip_next"))
        self.next_layer_btn.clicked.connect(self._select_next_layer)
        self.next_layer_btn.setFixedWidth(75)
        self.next_layer_btn.setFixedHeight(32)
        nav_layout.addWidget(self.next_layer_btn)
        
        # Add stretch to push buttons to center
        nav_layout.addStretch(1)
        
        # Add navigation buttons to layout
        layout.addLayout(nav_layout)
        
        # File information
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setMinimumHeight(120)
        self.info_display.setMaximumHeight(150)
        self.info_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', monospace;
                font-size: 11px;
                line-height: 1.4;
                padding: 8px;
            }
        """)
        layout.addWidget(self.info_display)
        
        # Disable buttons initially
        self._update_button_states(False)
        
        # Common button style
        button_style = """
            QPushButton {
                padding: 6px 10px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 80px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:pressed {
                background: #2472a4;
            }
            QPushButton:disabled {
                background: #bdc3c7;
            }
            QPushButton:checked {
                background: #27ae60;
            }
            QPushButton:checked:hover {
                background: #219a52;
            }
        """
        
        # Navigation button style (more compact)
        nav_button_style = """
            QPushButton {
                padding: 4px 8px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 70px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:pressed {
                background: #2472a4;
            }
            QPushButton:disabled {
                background: #bdc3c7;
            }
            QPushButton:checked {
                background: #27ae60;
            }
            QPushButton:checked:hover {
                background: #219a52;
            }
        """
        
        # Apply styles
        self.select_btn.setStyleSheet(button_style)
        self.select_all_btn.setStyleSheet(button_style)
        self.clear_all_btn.setStyleSheet(button_style)
        
        # Apply navigation button style
        self.prev_layer_btn.setStyleSheet(nav_button_style)
        self.next_layer_btn.setStyleSheet(nav_button_style)
        self.fill_btn.setStyleSheet(nav_button_style)
    
    def _tr(self, key):
        """Translate text using current language"""
        return Translations.get(key, self.current_language)
    
    def update_language(self, language):
        """Update UI language"""
        self.current_language = language
        
        # Update button texts
        self.select_btn.setText(self._tr("open_file"))
        self.select_btn.setToolTip(self._tr("tooltip_open_file"))
        self.select_all_btn.setText(self._tr("select_all"))
        self.select_all_btn.setToolTip(self._tr("tooltip_select_all"))
        self.clear_all_btn.setText(self._tr("clear_all"))
        self.clear_all_btn.setToolTip(self._tr("tooltip_clear_all"))
        self.prev_layer_btn.setText(self._tr("prev"))
        self.prev_layer_btn.setToolTip(self._tr("tooltip_prev"))
        self.fill_btn.setText(self._tr("fill"))
        self.fill_btn.setToolTip(self._tr("tooltip_fill"))
        self.next_layer_btn.setText(self._tr("next"))
        self.next_layer_btn.setToolTip(self._tr("tooltip_next"))
        
        # Update layer tree header
        self.layer_tree.setHeaderLabel(self._tr("layers"))
        
        # Update info display if there's content
        if self.dxf_handler.doc:
            self._update_info_display_with_current_language()
    
    def _update_button_states(self, enabled=True):
        """Update button active/inactive states"""
        self.select_all_btn.setEnabled(enabled)
        self.clear_all_btn.setEnabled(enabled)
        self.prev_layer_btn.setEnabled(enabled)
        self.next_layer_btn.setEnabled(enabled)
        self.fill_btn.setEnabled(enabled)
    
    def _select_all_layers(self):
        """Select all layers"""
        root = self.layer_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, Qt.CheckState.Checked)
    
    def _clear_all_layers(self):
        """Clear all layer selections"""
        root = self.layer_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, Qt.CheckState.Unchecked)
    
    def _select_previous_layer(self):
        """Show previous layer, hide others"""
        current_item = self.layer_tree.currentItem()
        if not current_item:
            return
            
        current_index = self.layer_tree.indexOfTopLevelItem(current_item)
        if current_index > 0:
            # Set current layer font to normal
            self._set_normal_layer(current_item)
            
            # Hide all layers
            self._hide_all_layers()
            
            # Show previous layer and make bold
            prev_item = self.layer_tree.topLevelItem(current_index - 1)
            self.layer_tree.setCurrentItem(prev_item)
            prev_item.setCheckState(0, Qt.CheckState.Checked)
            self._set_bold_layer(prev_item)
    
    def _select_next_layer(self):
        """Show next layer, hide others"""
        current_item = self.layer_tree.currentItem()
        if not current_item:
            return
            
        current_index = self.layer_tree.indexOfTopLevelItem(current_item)
        if current_index < self.layer_tree.topLevelItemCount() - 1:
            # Set current layer font to normal
            self._set_normal_layer(current_item)
            
            # Hide all layers
            self._hide_all_layers()
            
            # Show next layer and make bold
            next_item = self.layer_tree.topLevelItem(current_index + 1)
            self.layer_tree.setCurrentItem(next_item)
            next_item.setCheckState(0, Qt.CheckState.Checked)
            self._set_bold_layer(next_item)
    
    def _select_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, self._tr("select_dxf_file"), "", self._tr("dxf_files")
        )
        if filepath:
            try:
                info = self.dxf_handler.load_file(filepath)
                self._update_info_display(info)
                self._update_layer_tree()
                self.file_loaded.emit(filepath)
            except Exception as e:
                self.info_display.setText(f"{self._tr('error')}: {str(e)}")
    
    def _update_layer_tree(self):
        self.layer_tree.clear()
        if not self.dxf_handler.doc:
            self._update_button_states(False)
            return
            
        # Get all layers except Defpoints and sort alphabetically
        layers = [
            layer for layer in self.dxf_handler.doc.layers 
            if layer.dxf.name.lower() != 'defpoints'
        ]
        layers.sort(key=lambda x: x.dxf.name.lower())
        
        for layer in layers:
            color = self._get_layer_color(layer)
            item = LayerItem(layer.dxf.name, color)
            item.setCheckState(0, Qt.CheckState.Checked)
            self.layer_tree.addTopLevelItem(item)
        
        # Enable buttons when layers are loaded
        self._update_button_states(True)
        
        # Select first layer and make it bold
        if self.layer_tree.topLevelItemCount() > 0:
            first_item = self.layer_tree.topLevelItem(0)
            self.layer_tree.setCurrentItem(first_item)
            self._set_bold_layer(first_item)
    
    def _get_layer_color(self, layer):
        try:
            # First check RGB value
            if layer.rgb is not None:
                return QColor(*layer.rgb)
            
            # Check ACI color
            if hasattr(layer.dxf, 'color'):
                color_index = layer.dxf.color
                if color_index >= 0:
                    return self._aci_to_rgb(color_index)
        except Exception as e:
            print(f"{self._tr('color_conversion_error')}: {str(e)}")
        
        return QColor(255, 255, 255)  # Default white
    
    def _aci_to_rgb(self, color_index):
        """Convert AutoCAD Color Index (ACI) to RGB"""
        try:
            # AutoCAD standard color table (extended)
            aci_colors = {
                0: (0, 0, 0),       # ByBlock (Black)
                1: (255, 0, 0),     # Red
                2: (255, 255, 0),   # Yellow
                3: (0, 255, 0),     # Green
                4: (0, 255, 255),   # Cyan
                5: (0, 0, 255),     # Blue
                6: (255, 0, 255),   # Magenta
                7: (0, 0, 0),       # Black/White
                8: (128, 128, 128), # Dark Gray
                9: (192, 192, 192), # Light Gray
                10: (255, 0, 0),    # Red
                11: (255, 127, 127),
                12: (204, 0, 0),
                13: (204, 102, 102),
                14: (153, 0, 0),
                15: (153, 76, 76),
                20: (255, 255, 0),  # Yellow
                21: (255, 255, 127),
                22: (204, 204, 0),
                23: (204, 204, 102),
                24: (153, 153, 0),
                25: (153, 153, 76),
                30: (0, 255, 0),    # Green
                31: (127, 255, 127),
                32: (0, 204, 0),
                33: (102, 204, 102),
                34: (0, 153, 0),
                35: (76, 153, 76),
                40: (0, 255, 255),  # Cyan
                41: (127, 255, 255),
                42: (0, 204, 204),
                43: (102, 204, 204),
                44: (0, 153, 153),
                45: (76, 153, 153),
                50: (0, 0, 255),    # Blue
                51: (127, 127, 255),
                52: (0, 0, 204),
                53: (102, 102, 204),
                54: (0, 0, 153),
                55: (76, 76, 153),
                60: (255, 0, 255),  # Magenta
                61: (255, 127, 255),
                62: (204, 0, 204),
                63: (204, 102, 204),
                64: (153, 0, 153),
                65: (153, 76, 153),
                250: (238, 238, 238),
                251: (217, 217, 217),
                252: (196, 196, 196),
                253: (175, 175, 175),
                254: (154, 154, 154),
                255: (133, 133, 133),
                256: (0, 0, 0),     # ByLayer (Black)
            }
            
            # Use color from table if index exists
            if color_index in aci_colors:
                return QColor(*aci_colors[color_index])
            
            # Use AutoCAD's color algorithm if index not in table
            if 0 <= color_index <= 255:
                # AutoCAD color algorithm
                base_index = (color_index - 1) // 10 * 10 + 1
                if base_index in aci_colors:
                    base_color = aci_colors[base_index]
                    # Calculate tone variation
                    factor = 1.0 - (0.1 * ((color_index - base_index) % 10))
                    return QColor(
                        int(base_color[0] * factor),
                        int(base_color[1] * factor),
                        int(base_color[2] * factor)
                    )
            
            # Default color if no match found
            return QColor(0, 0, 0)  # Default black
            
        except Exception as e:
            print(f"{self._tr('color_conversion_error')} (ACI: {color_index}): {str(e)}")
            return QColor(0, 0, 0)  # Black in case of error
    
    def _on_layer_visibility_changed(self, item, column):
        if isinstance(item, LayerItem):
            is_visible = item.checkState(0) == Qt.CheckState.Checked
            self.layer_visibility_changed.emit(item.layer_name, is_visible)
    
    def _update_info_display(self, info):
        # Show layer count excluding Defpoints
        actual_layer_count = sum(
            1 for layer in self.dxf_handler.doc.layers 
            if layer.dxf.name.lower() != 'defpoints'
        )
        
        text = f"{self._tr('file')}: {info.filename}\n"
        text += f"{self._tr('layer_count')}: {actual_layer_count}\n\n"
        text += f"{self._tr('geometry_types')}:\n"
        
        # Exclude entities in Defpoints layer
        filtered_counts = {
            entity_type: count 
            for entity_type, count in info.entity_counts.items()
        }
        
        for entity_type, count in filtered_counts.items():
            text += f"- {entity_type}: {count}\n"
        
        self.info_display.setText(text)
    
    def _update_info_display_with_current_language(self):
        """Update info display with current language"""
        if self.dxf_handler.doc and self.dxf_handler.current_file:
            info = self.dxf_handler.get_info()
            self._update_info_display(info)
    
    def _hide_all_layers(self):
        """Hide all layers"""
        root = self.layer_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, Qt.CheckState.Unchecked) 
    
    def _set_bold_layer(self, item):
        """Make layer font bold (Show current layer)"""
        font = item.font(0)
        font.setBold(True)
        item.setFont(0, font)
    
    def _set_normal_layer(self, item):
        """Set layer font to normal"""
        font = item.font(0)
        font.setBold(False)
        item.setFont(0, font) 
    
    def _toggle_fill(self):
        """Toggle fill mode on/off"""
        if hasattr(self, 'canvas'):
            self.canvas.toggle_fill_mode() 
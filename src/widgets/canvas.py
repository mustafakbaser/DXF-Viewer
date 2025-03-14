from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QRubberBand, QApplication,
                           QMenu, QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
                           QLabel, QColorDialog)
from PyQt6.QtCore import Qt, QPointF, QRectF, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
import ezdxf
from ezdxf.math import Vec2
import math
import numpy as np

class EntityPropertiesDialog(QDialog):
    def __init__(self, entity, parent=None):
        super().__init__(parent)
        self.entity = entity
        self.setWindowTitle("Entity Properties")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                padding: 8px 15px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:pressed {
                background: #2472a4;
            }
            QDialogButtonBox {
                margin-top: 15px;
            }
        """)
        self._init_ui()
    
    def _init_ui(self):
        layout = QFormLayout(self)
        
        # Basic properties
        self.type_label = QLabel(f"Type: {self.entity.dxftype()}")
        layout.addRow(self.type_label)
        
        # Layer
        self.layer_edit = QLineEdit(self.entity.dxf.layer)
        layout.addRow("Layer:", self.layer_edit)
        
        # Color picker
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self._select_color)
        if hasattr(self.entity.dxf, 'color'):
            current_color = self.entity.rgb or (0, 0, 0)
            self.current_color = QColor(*current_color)
            self._update_color_button()
        layout.addRow("Color:", self.color_button)
        
        # Entity specific properties
        self._add_specific_properties(layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def _add_specific_properties(self, layout):
        entity_type = self.entity.dxftype()
        
        if entity_type == 'LINE':
            # Start point
            start = self.entity.dxf.start
            self.start_x = QLineEdit(str(start[0]))
            self.start_y = QLineEdit(str(start[1]))
            layout.addRow("Start X:", self.start_x)
            layout.addRow("Start Y:", self.start_y)
            
            # End point
            end = self.entity.dxf.end
            self.end_x = QLineEdit(str(end[0]))
            self.end_y = QLineEdit(str(end[1]))
            layout.addRow("End X:", self.end_x)
            layout.addRow("End Y:", self.end_y)
            
        elif entity_type in ('CIRCLE', 'ARC'):
            # Center point
            center = self.entity.dxf.center
            self.center_x = QLineEdit(str(center[0]))
            self.center_y = QLineEdit(str(center[1]))
            layout.addRow("Center X:", self.center_x)
            layout.addRow("Center Y:", self.center_y)
            
            # Radius
            self.radius = QLineEdit(str(self.entity.dxf.radius))
            layout.addRow("Radius:", self.radius)
            
            if entity_type == 'ARC':
                # Start and end angles
                self.start_angle = QLineEdit(str(math.degrees(self.entity.dxf.start_angle)))
                self.end_angle = QLineEdit(str(math.degrees(self.entity.dxf.end_angle)))
                layout.addRow("Start Angle:", self.start_angle)
                layout.addRow("End Angle:", self.end_angle)
    
    def _select_color(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self._update_color_button()
    
    def _update_color_button(self):
        self.color_button.setStyleSheet(
            f"background-color: {self.current_color.name()};"
            f"color: {'white' if self.current_color.value() < 128 else 'black'};"
        )
        self.color_button.setText(self.current_color.name())

class DXFCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self.scale = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.doc = None
        self.entities = []
        self.bounds = None
        self.hidden_layers = set()  # Track hidden layers
        
        # Variables for selection
        self.selected_entities = set()
        self.selection_mode = False
        self.rubber_band = None
        self.selection_start = None
        self.highlight_color = QColor(52, 152, 219, 100)  # Modern blue color
        
        # Variable for fill mode
        self.fill_mode = False
        
        # Background color
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def _init_ui(self):
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for maximum drawing area
        self.setLayout(layout)
        self.setMouseTracking(True)  # Track mouse movements
        
    def load_dxf(self, filepath):
        try:
            self.doc = ezdxf.readfile(filepath)
            self.entities = list(self.doc.modelspace())
            
            # Print entity types and colors for debugging
            for entity in self.entities:
                color_info = ""
                if hasattr(entity.dxf, 'color'):
                    color_info = f"ACI: {entity.dxf.color}"
                if hasattr(entity, 'rgb') and entity.rgb:
                    color_info += f", RGB: {entity.rgb}"
                
                print(f"Entity: {entity.dxftype()}, "
                      f"Layer: {entity.dxf.layer}, "
                      f"Color: {color_info}")
            
            self._calculate_bounds()
            self._center_view()
            self.update()
        except Exception as e:
            print(f"DXF loading error: {str(e)}")
    
    def _calculate_bounds(self):
        if not self.entities:
            return
        
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for entity in self.entities:
            points = []
            entity_type = entity.dxftype()
            
            if entity_type == 'LINE':
                points = [entity.dxf.start, entity.dxf.end]
            elif entity_type == 'CIRCLE':
                center = entity.dxf.center
                radius = entity.dxf.radius
                points = [
                    (center[0] - radius, center[1] - radius),
                    (center[0] + radius, center[1] + radius)
                ]
            elif entity_type == 'ARC':
                center = entity.dxf.center
                radius = entity.dxf.radius
                points = [
                    (center[0] - radius, center[1] - radius),
                    (center[0] + radius, center[1] + radius)
                ]
            elif entity_type == 'LWPOLYLINE':
                points = list(entity.get_points('xy'))
            elif entity_type == 'POLYLINE':
                points = [vertex.dxf.location for vertex in entity.vertices]
            elif entity_type == 'SPLINE':
                try:
                    # Spline points
                    spline_points = entity.construction_tool().get_points(100)
                    points = [(p.x, p.y) for p in spline_points]
                    
                    # Also add control points
                    points.extend(entity.control_points)
                    
                    # If fit points exist, add them too
                    if hasattr(entity, 'fit_points') and entity.fit_points:
                        points.extend(entity.fit_points)
                        
                except Exception as e:
                    print(f"Spline bounds calculation error: {str(e)}")
                    points = []
            elif entity_type == 'ELLIPSE':
                center = entity.dxf.center
                major_axis = entity.dxf.major_axis
                ratio = entity.dxf.ratio
                major_radius = math.sqrt(major_axis[0]**2 + major_axis[1]**2)
                minor_radius = major_radius * ratio
                points = [
                    (center[0] - major_radius, center[1] - minor_radius),
                    (center[0] + major_radius, center[1] + minor_radius)
                ]
            elif entity_type == 'TEXT':
                pos = entity.dxf.insert
                height = entity.dxf.height
                points = [pos, (pos[0] + len(entity.dxf.text) * height, pos[1] + height)]
            elif entity_type == 'POINT':
                pos = entity.dxf.location
                points = [pos]
            
            for point in points:
                min_x = min(min_x, point[0])
                max_x = max(max_x, point[0])
                min_y = min(min_y, point[1])
                max_y = max(max_y, point[1])
        
        self.bounds = (min_x, min_y, max_x, max_y)
    
    def _center_view(self):
        if not self.bounds:
            return
            
        width = self.width()
        height = self.height()
        
        # Calculate drawing bounds
        dx = self.bounds[2] - self.bounds[0]
        dy = self.bounds[3] - self.bounds[1]
        
        # Add padding (15% of drawing area)
        padding_factor = 0.15
        padding_x = dx * padding_factor
        padding_y = dy * padding_factor
        
        # Padded total dimensions
        total_width = dx + 2 * padding_x
        total_height = dy + 2 * padding_y
        
        # Calculate scaling factor
        scale_x = width / total_width if total_width != 0 else 1
        scale_y = height / total_height if total_height != 0 else 1
        
        # Use smallest scale (best fit)
        self.scale = max(min(scale_x, scale_y), 0.0001)
        
        # Calculate center points
        world_center_x = self.bounds[0] + dx/2
        world_center_y = self.bounds[1] + dy/2
        
        # Viewport center
        viewport_center_x = width/2
        viewport_center_y = height/2
        
        # Calculate pan values
        self.pan_x = viewport_center_x - (world_center_x * self.scale)
        self.pan_y = viewport_center_y + (world_center_y * self.scale)  # Y axis is inverted
        
        # Save minimum zoom level
        self.min_scale = self.scale * 0.5
    
    def paintEvent(self, event):
        if not self.doc:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set coordinate system
        painter.translate(self.pan_x, self.pan_y)
        painter.scale(self.scale, -self.scale)
        
        # Draw entities
        for entity in self.entities:
            self._draw_entity(painter, entity)
    
    def _draw_entity(self, painter, entity):
        if entity.dxf.layer in self.hidden_layers:
            return
        
        entity_type = entity.dxftype()
        
        # Color settings
        color = self._get_entity_color(entity)
        pen = QPen(color)
        pen.setWidth(0)
        if hasattr(entity.dxf, 'linetype'):
            self._apply_linetype(pen, entity.dxf.linetype)
        
        # Highlight selected entities
        if entity in self.selected_entities:
            pen = QPen(self.highlight_color)
            pen.setWidth(3)
        
        painter.setPen(pen)
        
        # Fill settings
        if self.fill_mode and entity.dxf.layer != "0":
            brush_color = QColor(color)
            brush_color.setAlpha(100)  # Semi-transparent fill
            painter.setBrush(QBrush(brush_color))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Draw based on entity type
        if entity_type == 'LINE':
            self._draw_line(painter, entity)
        elif entity_type == 'CIRCLE':
            self._draw_circle_with_fill(painter, entity)
        elif entity_type == 'ARC':
            self._draw_arc(painter, entity)
        elif entity_type == 'LWPOLYLINE':
            self._draw_polyline_with_fill(painter, entity)
        elif entity_type == 'POLYLINE':
            self._draw_polyline_with_fill(painter, entity)
        elif entity_type == 'SPLINE':
            self._draw_spline_with_fill(painter, entity)
        elif entity_type == 'ELLIPSE':
            self._draw_ellipse(painter, entity)
        elif entity_type == 'TEXT':
            self._draw_text(painter, entity)
        elif entity_type == 'POINT':
            self._draw_point(painter, entity)
    
    def _draw_polyline_with_fill(self, painter, entity):
        try:
            # Get points based on entity type
            if entity.dxftype() == 'LWPOLYLINE':
                points = list(entity.get_points('xy'))
                # Check for closed condition for LWPOLYLINE
                is_closed = entity.dxf.flags & 1
            else:  # POLYLINE
                points = [(vertex.dxf.location[0], vertex.dxf.location[1]) 
                         for vertex in entity.vertices]
                # Check for closed condition for POLYLINE
                is_closed = entity.is_closed
            
            if len(points) < 2:
                return
            
            # Create drawing path
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            
            for point in points[1:]:
                path.lineTo(point[0], point[1])
            
            # Close path for closed polyline
            if is_closed:
                path.closeSubpath()
            
            # Draw
            painter.drawPath(path)
            
        except Exception as e:
            print(f"Polyline drawing error ({entity.dxftype()}): {str(e)}")
    
    def _draw_circle_with_fill(self, painter, entity):
        center = entity.dxf.center
        radius = entity.dxf.radius
        painter.drawEllipse(
            QPointF(center[0], center[1]),
            radius, radius
        )
    
    def _draw_spline_with_fill(self, painter, entity):
        try:
            spline_points = entity.construction_tool().get_points(100)
            points = [(p.x, p.y) for p in spline_points]
            
            if len(points) < 2:
                return
            
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            
            for point in points[1:]:
                path.lineTo(point[0], point[1])
            
            # Close path if spline is closed
            if entity.closed:
                path.closeSubpath()
            
            painter.drawPath(path)
            
        except Exception as e:
            print(f"Spline drawing error: {str(e)}")
    
    def _draw_regular_entity(self, painter, entity):
        """Draw normal entities without fill"""
        entity_type = entity.dxftype()
        
        if entity_type == 'LINE':
            self._draw_line(painter, entity)
        elif entity_type == 'ARC':
            self._draw_arc(painter, entity)
        elif entity_type == 'ELLIPSE':
            self._draw_ellipse(painter, entity)
        elif entity_type == 'TEXT':
            self._draw_text(painter, entity)
        elif entity_type == 'POINT':
            self._draw_point(painter, entity)
    
    def _draw_line(self, painter, entity):
        start = entity.dxf.start
        end = entity.dxf.end
        painter.drawLine(
            QPointF(start[0], start[1]),
            QPointF(end[0], end[1])
        )
    
    def _draw_arc(self, painter, entity):
        center = entity.dxf.center
        radius = entity.dxf.radius
        start_angle = math.degrees(entity.dxf.start_angle)
        end_angle = math.degrees(entity.dxf.end_angle)
        
        rect = QRectF(
            center[0] - radius,
            center[1] - radius,
            radius * 2,
            radius * 2
        )
        painter.drawArc(
            rect,
            int(-start_angle * 16),
            int(-(end_angle - start_angle) * 16)
        )
    
    def _draw_ellipse(self, painter, entity):
        center = entity.dxf.center
        major_axis = entity.dxf.major_axis
        ratio = entity.dxf.ratio
        
        # Calculate ellipse parameters
        major_radius = math.sqrt(major_axis[0]**2 + major_axis[1]**2)
        minor_radius = major_radius * ratio
        
        # Calculate rotation angle
        rotation = math.degrees(math.atan2(major_axis[1], major_axis[0]))
        
        painter.save()
        painter.translate(center[0], center[1])
        painter.rotate(rotation)
        painter.drawEllipse(QPointF(0, 0), major_radius, minor_radius)
        painter.restore()
    
    def _draw_text(self, painter, entity):
        pos = entity.dxf.insert
        text = entity.dxf.text
        height = entity.dxf.height
        
        # Font settings
        font = painter.font()
        font.setPointSizeF(height * self.scale)
        painter.setFont(font)
        
        # Text alignment
        flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
        
        painter.save()
        painter.translate(pos[0], pos[1])
        if hasattr(entity.dxf, 'rotation'):
            painter.rotate(-entity.dxf.rotation)
        painter.scale(1, -1)  # Correct text for inverted Y axis
        painter.drawText(QPointF(0, 0), text)
        painter.restore()
    
    def _draw_point(self, painter, entity):
        pos = entity.dxf.location
        size = 5 / self.scale  # Fixed screen size
        
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        if entity in self.selected_entities:
            painter.setBrush(self.highlight_color)
        painter.drawEllipse(QPointF(pos[0], pos[1]), size, size)
        painter.restore()
    
    def _get_entity_color(self, entity):
        try:
            # First check entity's own color
            if hasattr(entity.dxf, 'color') and entity.dxf.color is not None:
                color_index = entity.dxf.color
                
                # If layer (256) or by block (0), use layer color
                if color_index == 256 or color_index == 0:  
                    layer = self.doc.layers.get(entity.dxf.layer)
                    if layer and hasattr(layer.dxf, 'color'):
                        color_index = layer.dxf.color
                        # If layer has RGB value, use it
                        if layer.rgb is not None:
                            color = QColor(*layer.rgb)
                            # Convert white to black
                            if color.red() == 255 and color.green() == 255 and color.blue() == 255:
                                return QColor(0, 0, 0)
                            return color
                
                # If RGB value exists, use it
                if hasattr(entity, 'rgb') and entity.rgb is not None:
                    color = QColor(*entity.rgb)
                    # Convert white to black
                    if color.red() == 255 and color.green() == 255 and color.blue() == 255:
                        return QColor(0, 0, 0)
                    return color
                # Convert ACI color code to RGB
                elif color_index >= 0:
                    color = self._aci_to_rgb(color_index)
                    # Convert white to black
                    if color.red() == 255 and color.green() == 255 and color.blue() == 255:
                        return QColor(0, 0, 0)
                    return color
            
            # Layer color
            layer = self.doc.layers.get(entity.dxf.layer)
            if layer:
                if layer.rgb is not None:
                    color = QColor(*layer.rgb)
                    # Convert white to black
                    if color.red() == 255 and color.green() == 255 and color.blue() == 255:
                        return QColor(0, 0, 0)
                    return color
                elif hasattr(layer.dxf, 'color') and layer.dxf.color >= 0:
                    color = self._aci_to_rgb(layer.dxf.color)
                    # Convert white to black
                    if color.red() == 255 and color.green() == 255 and color.blue() == 255:
                        return QColor(0, 0, 0)
                    return color
        except Exception as e:
            print(f"Color conversion error: {str(e)}")
        
        return QColor(0, 0, 0)  # Default color is now black
    
    def _aci_to_rgb(self, color_index):
        """
        AutoCAD Color Index (ACI) color to RGB conversion
        """
        # AutoCAD standard color table
        aci_colors = {
            0: (0, 0, 0),       # ByBlock (Black)
            1: (255, 0, 0),     # Red
            2: (255, 255, 0),   # Yellow
            3: (0, 255, 0),     # Green
            4: (0, 255, 255),   # Cyan
            5: (0, 0, 255),     # Blue
            6: (255, 0, 255),   # Magenta
            7: (0, 0, 0),       # White instead of Black
            8: (128, 128, 128), # Dark Gray
            9: (192, 192, 192), # Light Gray
            256: (0, 0, 0),     # ByLayer (Black)
        }
        
        # Color calculation for special index values
        if color_index not in aci_colors:
            if 0 <= color_index <= 255:
                # More advanced color calculation algorithm
                hue = (color_index % 6) * 60  # 0-360 HSV color tone
                sat = 1.0  # Saturation
                val = min(1.0, (color_index % 25) / 24.0)  # Brightness
                
                # HSV to RGB conversion
                c = val * sat
                x = c * (1 - abs((hue / 60) % 2 - 1))
                m = val - c
                
                if 0 <= hue < 60:
                    r, g, b = c, x, 0
                elif 60 <= hue < 120:
                    r, g, b = x, c, 0
                elif 120 <= hue < 180:
                    r, g, b = 0, c, x
                elif 180 <= hue < 240:
                    r, g, b = 0, x, c
                elif 240 <= hue < 300:
                    r, g, b = x, 0, c
                else:
                    r, g, b = c, 0, x
                
                return QColor(
                    int((r + m) * 255),
                    int((g + m) * 255),
                    int((b + m) * 255)
                )
        
        # Get color from standard color table
        rgb = aci_colors.get(color_index, (0, 0, 0))
        return QColor(*rgb)
    
    def _apply_linetype(self, pen, linetype_name):
        if linetype_name == 'CONTINUOUS':
            pen.setStyle(Qt.PenStyle.SolidLine)
        elif linetype_name == 'DASHED':
            pen.setStyle(Qt.PenStyle.DashLine)
        elif linetype_name == 'DOTTED':
            pen.setStyle(Qt.PenStyle.DotLine)
        elif linetype_name == 'DASHDOT':
            pen.setStyle(Qt.PenStyle.DashDotLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)
    
    def wheelEvent(self, event):
        # Zoom based on mouse position
        old_pos = event.position()
        old_scene_pos = self._screen_to_world(old_pos)
        
        # Calculate zoom factor
        delta = event.angleDelta().y()
        zoom_factor = 1.1  # More accurate zoom for this
        
        if delta > 0:
            new_scale = self.scale * zoom_factor
        else:
            new_scale = self.scale / zoom_factor
        
        # Check minimum and maximum zoom limits
        max_scale = self.min_scale * 20  # Maximum 20x zoom
        new_scale = max(min(new_scale, max_scale), self.min_scale)
        
        # Apply new scale
        self.scale = new_scale
        
        # Keep mouse position for zoom
        new_scene_pos = self._screen_to_world(old_pos)
        self.pan_x += (new_scene_pos[0] - old_scene_pos[0]) * self.scale
        self.pan_y += (new_scene_pos[1] - old_scene_pos[1]) * self.scale
        
        self.update()
    
    def _screen_to_world(self, pos):
        # Convert screen coordinates to world coordinates
        wx = (pos.x() - self.pan_x) / self.scale
        wy = (pos.y() - self.pan_y) / self.scale
        return (wx, wy)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Selection mode
                self.selection_mode = True
                self.selection_start = event.pos()
                if not self.rubber_band:
                    self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
                # Start selection area
                self.rubber_band.setGeometry(
                    QRect(self.selection_start, self.selection_start)
                )
                self.rubber_band.show()
            else:
                # Pan mode
                self.last_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.selection_mode and self.rubber_band:
            # Create rectangle between two points
            rect = QRect(self.selection_start, event.pos()).normalized()
            self.rubber_band.setGeometry(rect)
        elif event.buttons() & Qt.MouseButton.LeftButton:
            # Pan operation
            diff = event.pos() - self.last_pos
            self.pan_x += diff.x()
            self.pan_y += diff.y()
            self.last_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.selection_mode:
            if self.rubber_band:
                # Get selection area
                selection_rect = self.rubber_band.geometry()
                self.rubber_band.hide()
                
                # Find entities in selection area
                self._select_entities_in_rect(selection_rect)
                
            self.selection_mode = False
            self.update()
    
    def _select_entities_in_rect(self, rect):
        # Convert screen coordinates to world coordinates
        top_left = self._screen_to_world(QPointF(rect.left(), rect.top()))
        bottom_right = self._screen_to_world(QPointF(rect.right(), rect.bottom()))
        
        selection_bounds = (
            min(top_left[0], bottom_right[0]),
            min(-top_left[1], -bottom_right[1]),  # Y coordinates are inverted
            max(top_left[0], bottom_right[0]),
            max(-top_left[1], -bottom_right[1])   # Y coordinates are inverted
        )
        
        # If CTRL key is not pressed, clear previous selection
        if not (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier):
            self.selected_entities.clear()
        
        # Find entities in selection area
        for entity in self.entities:
            if self._entity_in_bounds(entity, selection_bounds):
                self.selected_entities.add(entity)
    
    def _entity_in_bounds(self, entity, bounds):
        entity_type = entity.dxftype()
        
        if entity_type == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            return self._line_in_bounds(start, end, bounds)
            
        elif entity_type in ('CIRCLE', 'ARC'):
            center = entity.dxf.center
            radius = entity.dxf.radius
            return self._circle_in_bounds(center, radius, bounds)
            
        elif entity_type in ('LWPOLYLINE', 'POLYLINE'):
            points = list(entity.get_points('xy')) if entity_type == 'LWPOLYLINE' else \
                    [vertex.dxf.location for vertex in entity.vertices]
            return any(self._point_in_bounds(p, bounds) for p in points)
        
        return False
    
    def _line_in_bounds(self, start, end, bounds):
        # Simple collision check - may need to be improved
        return (self._point_in_bounds(start, bounds) or 
                self._point_in_bounds(end, bounds))
    
    def _circle_in_bounds(self, center, radius, bounds):
        return self._point_in_bounds(center, bounds)
    
    def _point_in_bounds(self, point, bounds):
        # Check if point is within bounds
        x, y = point[0], point[1]
        return (bounds[0] <= x <= bounds[2] and 
                bounds[1] <= y <= bounds[3])
    
    def set_layer_visibility(self, layer_name: str, visible: bool):
        if not visible:
            self.hidden_layers.add(layer_name)
        else:
            self.hidden_layers.discard(layer_name)
        self.update() 
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_entities.clear()
        self.update() 
    
    def _show_context_menu(self, position):
        menu = QMenu(self)
        
        # If there are selected entities
        if self.selected_entities:
            edit_action = menu.addAction("Edit Properties")
            edit_action.triggered.connect(self._edit_properties)
            
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(self._delete_selected)
            
            menu.addSeparator()
        
        # General menu items
        clear_selection = menu.addAction("Clear Selection")
        clear_selection.triggered.connect(self.clear_selection)
        
        menu.exec(self.mapToGlobal(position))
    
    def _edit_properties(self):
        # Currently only single entity editing
        if len(self.selected_entities) == 1:
            entity = next(iter(self.selected_entities))
            dialog = EntityPropertiesDialog(entity, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._update_entity_properties(entity, dialog)
                self.update()
    
    def _update_entity_properties(self, entity, dialog):
        # Update basic properties
        entity.dxf.layer = dialog.layer_edit.text()
        entity.rgb = (dialog.current_color.red(),
                     dialog.current_color.green(),
                     dialog.current_color.blue())
        
        # Update entity-specific properties
        entity_type = entity.dxftype()
        
        if entity_type == 'LINE':
            entity.dxf.start = (float(dialog.start_x.text()),
                              float(dialog.start_y.text()),
                              0)
            entity.dxf.end = (float(dialog.end_x.text()),
                            float(dialog.end_y.text()),
                            0)
            
        elif entity_type == 'CIRCLE':
            entity.dxf.center = (float(dialog.center_x.text()),
                               float(dialog.center_y.text()),
                               0)
            entity.dxf.radius = float(dialog.radius.text())
            
        elif entity_type == 'ARC':
            entity.dxf.center = (float(dialog.center_x.text()),
                               float(dialog.center_y.text()),
                               0)
            entity.dxf.radius = float(dialog.radius.text())
            entity.dxf.start_angle = math.radians(float(dialog.start_angle.text()))
            entity.dxf.end_angle = math.radians(float(dialog.end_angle.text()))
    
    def _delete_selected(self):
        for entity in self.selected_entities:
            self.entities.remove(entity)
            # Also remove from DXF file
            if self.doc and self.doc.modelspace():
                self.doc.modelspace().delete_entity(entity)
        
        self.selected_entities.clear()
        self.update() 
    
    def toggle_fill_mode(self):
        """Toggle fill mode on/off"""
        self.fill_mode = not self.fill_mode
        self.update() 
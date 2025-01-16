from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor
import ezdxf
from ezdxf.math import Vec2
import math

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
        self.hidden_layers = set()  # Gizli katmanları takip et
        
    def _init_ui(self):
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
    def load_dxf(self, filepath):
        try:
            self.doc = ezdxf.readfile(filepath)
            self.entities = list(self.doc.modelspace())
            self._calculate_bounds()
            self._center_view()
            self.update()
        except Exception as e:
            print(f"DXF yükleme hatası: {str(e)}")
    
    def _calculate_bounds(self):
        if not self.entities:
            return
        
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for entity in self.entities:
            entity_type = entity.dxftype()
            points = []
            
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
        
        # Çizim sınırlarını hesapla
        dx = self.bounds[2] - self.bounds[0]
        dy = self.bounds[3] - self.bounds[1]
        
        # Ölçeklendirme faktörünü hesapla
        scale_x = width / dx if dx != 0 else 1
        scale_y = height / dy if dy != 0 else 1
        self.scale = min(scale_x, scale_y) * 0.9  # %90 doluluk oranı
        
        # Merkeze konumlandır
        self.pan_x = width/2 - (self.bounds[0] + dx/2) * self.scale
        self.pan_y = height/2 - (self.bounds[1] + dy/2) * self.scale
    
    def paintEvent(self, event):
        if not self.doc:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Koordinat sistemini ayarla
        painter.translate(self.pan_x, self.pan_y)
        painter.scale(self.scale, -self.scale)
        
        # Entiteleri çiz
        for entity in self.entities:
            self._draw_entity(painter, entity)
    
    def _draw_entity(self, painter, entity):
        # Katman kontrolü
        if entity.dxf.layer in self.hidden_layers:
            return
        
        # Renk ve kalem ayarları
        color = self._get_entity_color(entity)
        pen = QPen(color)
        pen.setWidth(0)  # Sabit piksel genişliği
        
        # Çizgi tipi ayarları
        if hasattr(entity.dxf, 'linetype'):
            self._apply_linetype(pen, entity.dxf.linetype)
        
        painter.setPen(pen)
        
        entity_type = entity.dxftype()
        
        if entity_type == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            painter.drawLine(
                QPointF(start[0], start[1]),
                QPointF(end[0], end[1])
            )
            
        elif entity_type == 'CIRCLE':
            center = entity.dxf.center
            radius = entity.dxf.radius
            painter.drawEllipse(
                QPointF(center[0], center[1]),
                radius, radius
            )
            
        elif entity_type == 'ARC':
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
            
        elif entity_type == 'LWPOLYLINE':
            # LWPOLYLINE için points özelliğini kullan
            points = entity.get_points('xy')  # sadece x,y koordinatlarını al
            if len(points) < 2:
                return
                
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i + 1]
                painter.drawLine(
                    QPointF(start[0], start[1]),
                    QPointF(end[0], end[1])
                )
            
        elif entity_type == 'POLYLINE':
            # POLYLINE için vertices özelliğini kullan
            vertices = [vertex.dxf.location for vertex in entity.vertices]
            if len(vertices) < 2:
                return
                
            for i in range(len(vertices) - 1):
                start = vertices[i]
                end = vertices[i + 1]
                painter.drawLine(
                    QPointF(start[0], start[1]),
                    QPointF(end[0], end[1])
                )
    
    def _get_entity_color(self, entity):
        try:
            # Önce entity'nin kendi rengi
            if hasattr(entity.dxf, 'color') and entity.dxf.color is not None:
                rgb = entity.rgb
                if rgb is not None:
                    return QColor(*rgb)
            
            # Katman rengi
            layer = self.doc.layers.get(entity.dxf.layer)
            if layer and layer.rgb is not None:
                return QColor(*layer.rgb)
        except:
            pass
        
        return QColor(0, 0, 0)  # Varsayılan siyah
    
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
        # Fare pozisyonuna göre zoom
        old_pos = event.position()
        old_scene_pos = self._screen_to_world(old_pos)
        
        # Zoom faktörünü hesapla
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale *= 1.2
        else:
            self.scale /= 1.2
        
        # Fare pozisyonunu koruyarak zoom
        new_scene_pos = self._screen_to_world(old_pos)
        self.pan_x += (new_scene_pos[0] - old_scene_pos[0]) * self.scale
        self.pan_y += (new_scene_pos[1] - old_scene_pos[1]) * self.scale
        
        self.update()
    
    def _screen_to_world(self, pos):
        return (
            (pos.x() - self.pan_x) / self.scale,
            (pos.y() - self.pan_y) / -self.scale
        )
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_pos = event.pos()
            
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            diff = event.pos() - self.last_pos
            self.pan_x += diff.x()
            self.pan_y += diff.y()
            self.last_pos = event.pos()
            self.update() 
    
    def set_layer_visibility(self, layer_name: str, visible: bool):
        if not visible:
            self.hidden_layers.add(layer_name)
        else:
            self.hidden_layers.discard(layer_name)
        self.update() 
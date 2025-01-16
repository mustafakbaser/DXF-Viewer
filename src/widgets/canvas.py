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
        self.setWindowTitle("Nesne Özellikleri")
        self._init_ui()
    
    def _init_ui(self):
        layout = QFormLayout(self)
        
        # Temel özellikler
        self.type_label = QLabel(f"Tür: {self.entity.dxftype()}")
        layout.addRow(self.type_label)
        
        # Katman
        self.layer_edit = QLineEdit(self.entity.dxf.layer)
        layout.addRow("Katman:", self.layer_edit)
        
        # Renk seçici
        self.color_button = QPushButton("Renk Seç")
        self.color_button.clicked.connect(self._select_color)
        if hasattr(self.entity.dxf, 'color'):
            current_color = self.entity.rgb or (0, 0, 0)
            self.current_color = QColor(*current_color)
            self._update_color_button()
        layout.addRow("Renk:", self.color_button)
        
        # Entity tipine özel özellikler
        self._add_specific_properties(layout)
        
        # Butonlar
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
            # Başlangıç noktası
            start = self.entity.dxf.start
            self.start_x = QLineEdit(str(start[0]))
            self.start_y = QLineEdit(str(start[1]))
            layout.addRow("Başlangıç X:", self.start_x)
            layout.addRow("Başlangıç Y:", self.start_y)
            
            # Bitiş noktası
            end = self.entity.dxf.end
            self.end_x = QLineEdit(str(end[0]))
            self.end_y = QLineEdit(str(end[1]))
            layout.addRow("Bitiş X:", self.end_x)
            layout.addRow("Bitiş Y:", self.end_y)
            
        elif entity_type in ('CIRCLE', 'ARC'):
            # Merkez noktası
            center = self.entity.dxf.center
            self.center_x = QLineEdit(str(center[0]))
            self.center_y = QLineEdit(str(center[1]))
            layout.addRow("Merkez X:", self.center_x)
            layout.addRow("Merkez Y:", self.center_y)
            
            # Yarıçap
            self.radius = QLineEdit(str(self.entity.dxf.radius))
            layout.addRow("Yarıçap:", self.radius)
            
            if entity_type == 'ARC':
                # Başlangıç ve bitiş açıları
                self.start_angle = QLineEdit(str(math.degrees(self.entity.dxf.start_angle)))
                self.end_angle = QLineEdit(str(math.degrees(self.entity.dxf.end_angle)))
                layout.addRow("Başlangıç Açısı:", self.start_angle)
                layout.addRow("Bitiş Açısı:", self.end_angle)
    
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
        self.hidden_layers = set()  # Gizli katmanları takip et
        
        # Seçim için yeni değişkenler
        self.selected_entities = set()
        self.selection_mode = False
        self.rubber_band = None
        self.selection_start = None
        self.highlight_color = QColor(0, 120, 215, 100)  # Yarı saydam mavi
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def _init_ui(self):
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.setMouseTracking(True)  # Fare hareketlerini takip et
        
    def load_dxf(self, filepath):
        try:
            self.doc = ezdxf.readfile(filepath)
            self.entities = list(self.doc.modelspace())
            
            # Debug için entity tiplerini ve renklerini yazdır
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
            print(f"DXF yükleme hatası: {str(e)}")
    
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
                # Spline kontrol noktalarını kullan
                points = [cp for cp in entity.control_points]
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
        
        # Çizim sınırlarını hesapla
        dx = self.bounds[2] - self.bounds[0]
        dy = self.bounds[3] - self.bounds[1]
        
        # Padding ekle (çizim alanının %15'i kadar)
        padding_factor = 0.15
        padding_x = dx * padding_factor
        padding_y = dy * padding_factor
        
        # Padding'li toplam boyutlar
        total_width = dx + 2 * padding_x
        total_height = dy + 2 * padding_y
        
        # Ölçeklendirme faktörünü hesapla
        scale_x = width / total_width if total_width != 0 else 1
        scale_y = height / total_height if total_height != 0 else 1
        
        # En küçük ölçeği kullan (en iyi uyum için)
        self.scale = max(min(scale_x, scale_y), 0.0001)
        
        # Merkez noktaları hesapla
        world_center_x = self.bounds[0] + dx/2
        world_center_y = self.bounds[1] + dy/2
        
        # Viewport merkezi
        viewport_center_x = width/2
        viewport_center_y = height/2
        
        # Pan değerlerini hesapla
        self.pan_x = viewport_center_x - (world_center_x * self.scale)
        self.pan_y = viewport_center_y + (world_center_y * self.scale)  # Y ekseni ters olduğu için toplama
        
        # Minimum zoom seviyesini kaydet
        self.min_scale = self.scale * 0.5
    
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
        
        entity_type = entity.dxftype()
        
        # Seçili entiteleri vurgula
        if entity in self.selected_entities:
            pen = QPen(self.highlight_color)
            pen.setWidth(3)
            painter.setPen(pen)
        else:
            color = self._get_entity_color(entity)
            pen = QPen(color)
            pen.setWidth(0)
            if hasattr(entity.dxf, 'linetype'):
                self._apply_linetype(pen, entity.dxf.linetype)
            painter.setPen(pen)
        
        # Entity tipine göre çizim
        if entity_type == 'LINE':
            self._draw_line(painter, entity)
        elif entity_type == 'CIRCLE':
            self._draw_circle(painter, entity)
        elif entity_type == 'ARC':
            self._draw_arc(painter, entity)
        elif entity_type in ('LWPOLYLINE', 'POLYLINE'):
            self._draw_polyline(painter, entity)
        elif entity_type == 'SPLINE':
            self._draw_spline(painter, entity)
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
    
    def _draw_circle(self, painter, entity):
        center = entity.dxf.center
        radius = entity.dxf.radius
        if entity in self.selected_entities:
            painter.setBrush(QBrush(self.highlight_color.lighter(150)))
        painter.drawEllipse(
            QPointF(center[0], center[1]),
            radius, radius
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
    
    def _draw_polyline(self, painter, entity):
        if entity.dxftype() == 'LWPOLYLINE':
            points = list(entity.get_points('xy'))
        else:  # POLYLINE
            points = [vertex.dxf.location for vertex in entity.vertices]
        
        if len(points) < 2:
            return
        
        # Kapalı polyline için son noktayı ilk noktaya bağla
        if hasattr(entity.dxf, 'closed') and entity.dxf.closed:
            points.append(points[0])
        
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            painter.drawLine(
                QPointF(start[0], start[1]),
                QPointF(end[0], end[1])
            )
    
    def _draw_spline(self, painter, entity):
        try:
            # Spline'ı daha hassas noktalarla örnekle
            points = []
            params = np.linspace(0, 1, 100)  # 100 nokta ile örnekleme
            
            # Spline'ın fit noktalarını al
            if hasattr(entity, 'fit_points') and entity.fit_points:
                # Fit noktaları varsa onları kullan
                points = [point for point in entity.fit_points]
            else:
                # Kontrol noktalarını kullan
                points = [point for point in entity.control_points]
            
            if len(points) < 2:
                return
            
            # Çizim yolu oluştur
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            
            if len(points) == 2:
                # Sadece iki nokta varsa düz çizgi çiz
                path.lineTo(points[1][0], points[1][1])
            else:
                # Çoklu nokta varsa eğri çiz
                for i in range(1, len(points) - 2):
                    # Cubic bezier eğrisi kullan
                    path.cubicTo(
                        points[i][0], points[i][1],
                        (points[i][0] + points[i+1][0]) / 2, (points[i][1] + points[i+1][1]) / 2,
                        points[i+1][0], points[i+1][1]
                    )
                # Son noktaya bağlan
                path.lineTo(points[-1][0], points[-1][1])
            
            painter.drawPath(path)
            
        except Exception as e:
            print(f"Spline çizim hatası: {str(e)}")
    
    def _draw_ellipse(self, painter, entity):
        center = entity.dxf.center
        major_axis = entity.dxf.major_axis
        ratio = entity.dxf.ratio
        
        # Elips parametrelerini hesapla
        major_radius = math.sqrt(major_axis[0]**2 + major_axis[1]**2)
        minor_radius = major_radius * ratio
        
        # Dönüş açısını hesapla
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
        
        # Yazı tipi ayarları
        font = painter.font()
        font.setPointSizeF(height * self.scale)
        painter.setFont(font)
        
        # Metin hizalama
        flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
        
        painter.save()
        painter.translate(pos[0], pos[1])
        if hasattr(entity.dxf, 'rotation'):
            painter.rotate(-entity.dxf.rotation)
        painter.scale(1, -1)  # Y ekseni tersine çevrildiği için metni düzelt
        painter.drawText(QPointF(0, 0), text)
        painter.restore()
    
    def _draw_point(self, painter, entity):
        pos = entity.dxf.location
        size = 5 / self.scale  # Sabit ekran boyutu için ölçekle
        
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        if entity in self.selected_entities:
            painter.setBrush(self.highlight_color)
        painter.drawEllipse(QPointF(pos[0], pos[1]), size, size)
        painter.restore()
    
    def _get_entity_color(self, entity):
        try:
            # Önce entity'nin kendi rengi
            if hasattr(entity.dxf, 'color') and entity.dxf.color is not None:
                color_index = entity.dxf.color
                
                # ByLayer (256) veya ByBlock (0) ise katman rengini kullan
                if color_index == 256 or color_index == 0:  
                    layer = self.doc.layers.get(entity.dxf.layer)
                    if layer and hasattr(layer.dxf, 'color'):
                        color_index = layer.dxf.color
                        # Eğer katmanın RGB değeri varsa onu kullan
                        if layer.rgb is not None:
                            color = QColor(*layer.rgb)
                            # Beyazsa siyaha çevir
                            if color.red() == 255 and color.green() == 255 and color.blue() == 255:
                                return QColor(0, 0, 0)
                            return color
                
                # RGB değeri varsa onu kullan
                if hasattr(entity, 'rgb') and entity.rgb is not None:
                    color = QColor(*entity.rgb)
                    # Beyazsa siyaha çevir
                    if color.red() == 255 and color.green() == 255 and color.blue() == 255:
                        return QColor(0, 0, 0)
                    return color
                # ACI renk kodunu RGB'ye çevir
                elif color_index >= 0:
                    color = self._aci_to_rgb(color_index)
                    # Beyazsa siyaha çevir
                    if color.red() == 255 and color.green() == 255 and color.blue() == 255:
                        return QColor(0, 0, 0)
                    return color
            
            # Katman rengi
            layer = self.doc.layers.get(entity.dxf.layer)
            if layer:
                if layer.rgb is not None:
                    color = QColor(*layer.rgb)
                    # Beyazsa siyaha çevir
                    if color.red() == 255 and color.green() == 255 and color.blue() == 255:
                        return QColor(0, 0, 0)
                    return color
                elif hasattr(layer.dxf, 'color') and layer.dxf.color >= 0:
                    color = self._aci_to_rgb(layer.dxf.color)
                    # Beyazsa siyaha çevir
                    if color.red() == 255 and color.green() == 255 and color.blue() == 255:
                        return QColor(0, 0, 0)
                    return color
        except Exception as e:
            print(f"Renk dönüşüm hatası: {str(e)}")
        
        return QColor(0, 0, 0)  # Varsayılan renk artık siyah
    
    def _aci_to_rgb(self, color_index):
        """
        AutoCAD Color Index (ACI) rengini RGB'ye çevirme işlemleri
        """
        # AutoCAD standart renk tablosu
        aci_colors = {
            0: (0, 0, 0),       # ByBlock (Siyah)
            1: (255, 0, 0),     # Kırmızı
            2: (255, 255, 0),   # Sarı
            3: (0, 255, 0),     # Yeşil
            4: (0, 255, 255),   # Cyan
            5: (0, 0, 255),     # Mavi
            6: (255, 0, 255),   # Magenta
            7: (0, 0, 0),       # Beyaz yerine Siyah
            8: (128, 128, 128), # Koyu Gri
            9: (192, 192, 192), # Açık Gri
            256: (0, 0, 0),     # ByLayer (Siyah)
        }
        
        # Özel renk indeksleri için renk hesaplama
        if color_index not in aci_colors:
            if 0 <= color_index <= 255:
                # Daha gelişmiş renk hesaplama algoritması
                hue = (color_index % 6) * 60  # 0-360 arası HSV renk tonu
                sat = 1.0  # Doygunluk
                val = min(1.0, (color_index % 25) / 24.0)  # Parlaklık
                
                # HSV'den RGB'ye dönüşüm
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
        
        # Standart renk tablosundan rengi al
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
        # Fare pozisyonuna göre zoom
        old_pos = event.position()
        old_scene_pos = self._screen_to_world(old_pos)
        
        # Zoom faktörünü hesapla
        delta = event.angleDelta().y()
        zoom_factor = 1.1  # Daha hassas zoom için
        
        if delta > 0:
            new_scale = self.scale * zoom_factor
        else:
            new_scale = self.scale / zoom_factor
        
        # Minimum ve maksimum zoom sınırlarını kontrol et
        max_scale = self.min_scale * 20  # Maksimum 20x zoom
        new_scale = max(min(new_scale, max_scale), self.min_scale)
        
        # Yeni scale'i uygula
        self.scale = new_scale
        
        # Fare pozisyonunu koruyarak zoom
        new_scene_pos = self._screen_to_world(old_pos)
        self.pan_x += (new_scene_pos[0] - old_scene_pos[0]) * self.scale
        self.pan_y += (new_scene_pos[1] - old_scene_pos[1]) * self.scale
        
        self.update()
    
    def _screen_to_world(self, pos):
        # Ekran koordinatlarını dünya koordinatlarına çevir
        wx = (pos.x() - self.pan_x) / self.scale
        wy = (pos.y() - self.pan_y) / self.scale
        return (wx, wy)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Seçim modu
                self.selection_mode = True
                self.selection_start = event.pos()
                if not self.rubber_band:
                    self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
                # Seçim alanını başlat
                self.rubber_band.setGeometry(
                    QRect(self.selection_start, self.selection_start)
                )
                self.rubber_band.show()
            else:
                # Pan modu
                self.last_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.selection_mode and self.rubber_band:
            # İki nokta arasında dikdörtgen oluştur
            rect = QRect(self.selection_start, event.pos()).normalized()
            self.rubber_band.setGeometry(rect)
        elif event.buttons() & Qt.MouseButton.LeftButton:
            # Pan işlemi
            diff = event.pos() - self.last_pos
            self.pan_x += diff.x()
            self.pan_y += diff.y()
            self.last_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.selection_mode:
            if self.rubber_band:
                # Seçim alanını al
                selection_rect = self.rubber_band.geometry()
                self.rubber_band.hide()
                
                # Seçim alanındaki entiteleri bul
                self._select_entities_in_rect(selection_rect)
                
            self.selection_mode = False
            self.update()
    
    def _select_entities_in_rect(self, rect):
        # Ekran koordinatlarını dünya koordinatlarına çevir
        top_left = self._screen_to_world(QPointF(rect.left(), rect.top()))
        bottom_right = self._screen_to_world(QPointF(rect.right(), rect.bottom()))
        
        selection_bounds = (
            min(top_left[0], bottom_right[0]),
            min(-top_left[1], -bottom_right[1]),  # Y koordinatları ters çevrilmiş
            max(top_left[0], bottom_right[0]),
            max(-top_left[1], -bottom_right[1])   # Y koordinatları ters çevrilmiş
        )
        
        # CTRL tuşu basılı değilse önceki seçimi temizle
        if not (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier):
            self.selected_entities.clear()
        
        # Seçim alanı içindeki entiteleri bul
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
        # Basit çakışma kontrolü - geliştirilmesi gerekebilir
        return (self._point_in_bounds(start, bounds) or 
                self._point_in_bounds(end, bounds))
    
    def _circle_in_bounds(self, center, radius, bounds):
        return self._point_in_bounds(center, bounds)
    
    def _point_in_bounds(self, point, bounds):
        # Nokta sınırlar içinde mi kontrol et
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
        """Tüm seçimleri temizle"""
        self.selected_entities.clear()
        self.update() 
    
    def _show_context_menu(self, position):
        menu = QMenu(self)
        
        # Seçili nesne varsa
        if self.selected_entities:
            edit_action = menu.addAction("Özellikleri Düzenle")
            edit_action.triggered.connect(self._edit_properties)
            
            delete_action = menu.addAction("Sil")
            delete_action.triggered.connect(self._delete_selected)
            
            menu.addSeparator()
        
        # Genel menü öğeleri
        clear_selection = menu.addAction("Seçimi Temizle")
        clear_selection.triggered.connect(self.clear_selection)
        
        menu.exec(self.mapToGlobal(position))
    
    def _edit_properties(self):
        # Şimdilik sadece tek nesne düzenleme
        if len(self.selected_entities) == 1:
            entity = next(iter(self.selected_entities))
            dialog = EntityPropertiesDialog(entity, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._update_entity_properties(entity, dialog)
                self.update()
    
    def _update_entity_properties(self, entity, dialog):
        # Temel özellikleri güncelle
        entity.dxf.layer = dialog.layer_edit.text()
        entity.rgb = (dialog.current_color.red(),
                     dialog.current_color.green(),
                     dialog.current_color.blue())
        
        # Entity tipine özel özellikleri güncelle
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
            # DXF dosyasından da kaldır
            if self.doc and self.doc.modelspace():
                self.doc.modelspace().delete_entity(entity)
        
        self.selected_entities.clear()
        self.update() 
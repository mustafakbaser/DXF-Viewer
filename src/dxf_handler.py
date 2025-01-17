import ezdxf
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class DXFInfo:
    filename: str
    layer_count: int
    entity_counts: Dict[str, int]

class DXFHandler:
    def __init__(self):
        self.doc = None
        self.current_file = None

    def load_file(self, filepath: str) -> DXFInfo:
        try:
            self.doc = ezdxf.readfile(filepath)
            self.current_file = filepath
            
            # Defpoints hariç katman sayısını hesapla
            layer_count = sum(
                1 for layer in self.doc.layers 
                if layer.dxf.name.lower() != 'defpoints'
            )
            
            entity_counts = self._count_entities()
            
            return DXFInfo(
                filename=filepath.split('/')[-1],
                layer_count=layer_count,
                entity_counts=entity_counts
            )
        except Exception as e:
            raise Exception(f"DXF dosyası yüklenirken hata oluştu: {str(e)}")

    def _count_entities(self) -> Dict[str, int]:
        counts = {}
        if self.doc and self.doc.modelspace():
            for entity in self.doc.modelspace():
                # Defpoints katmanındaki entityleri sayma
                if entity.dxf.layer.lower() != 'defpoints':
                    entity_type = entity.dxftype()
                    counts[entity_type] = counts.get(entity_type, 0) + 1
        return counts 
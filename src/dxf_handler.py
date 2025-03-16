import ezdxf
from dataclasses import dataclass
from typing import List, Dict, Any
from translations import Translations

@dataclass
class DXFInfo:
    filename: str
    layer_count: int
    entity_counts: Dict[str, int]

class DXFHandler:
    def __init__(self, language=Translations.DEFAULT_LANGUAGE):
        self.doc = None
        self.current_file = None
        self.current_language = language

    def load_file(self, filepath: str) -> DXFInfo:
        try:
            self.doc = ezdxf.readfile(filepath)
            self.current_file = filepath
            
            # Calculate layer count excluding Defpoints
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
            error_msg = self._tr("dxf_loading_error")
            raise Exception(f"{error_msg}: {str(e)}")

    def _count_entities(self) -> Dict[str, int]:
        counts = {}
        if self.doc and self.doc.modelspace():
            for entity in self.doc.modelspace():
                # Don't count entities in Defpoints layer
                if entity.dxf.layer.lower() != 'defpoints':
                    entity_type = entity.dxftype()
                    counts[entity_type] = counts.get(entity_type, 0) + 1
        return counts
    
    def get_info(self) -> DXFInfo:
        """Get current DXF file info"""
        if not self.doc or not self.current_file:
            return None
        
        # Calculate layer count excluding Defpoints
        layer_count = sum(
            1 for layer in self.doc.layers 
            if layer.dxf.name.lower() != 'defpoints'
        )
        
        entity_counts = self._count_entities()
        
        return DXFInfo(
            filename=self.current_file.split('/')[-1],
            layer_count=layer_count,
            entity_counts=entity_counts
        )
    
    def update_language(self, language):
        """Update handler language"""
        self.current_language = language
    
    def _tr(self, key):
        """Translate text using current language"""
        return Translations.get(key, self.current_language) 
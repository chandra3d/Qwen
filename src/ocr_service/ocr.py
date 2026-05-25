"""
OCR Service for UI Understanding
Detects and reads text from screen captures
"""

import base64
from typing import List, Dict, Optional
from pathlib import Path
import json


class OCRService:
    """Optical Character Recognition service for UI text detection"""
    
    def __init__(self, engine: str = "easyocr"):
        self.engine = engine
        self.initialized = False
        self.reader = None
    
    def initialize(self):
        """Initialize OCR engine"""
        try:
            if self.engine == "easyocr":
                import easyocr
                self.reader = easyocr.Reader(['en'], gpu=False)
                self.initialized = True
                print("EasyOCR initialized successfully")
            elif self.engine == "paddleocr":
                from paddleocr import PaddleOCR
                self.reader = PaddleOCR(use_angle_cls=True, lang='en')
                self.initialized = True
                print("PaddleOCR initialized successfully")
            else:
                print(f"Unknown OCR engine: {self.engine}")
        except Exception as e:
            print(f"Failed to initialize OCR: {e}")
            self.initialized = False
    
    def extract_text_from_image(self, image_path: str) -> List[Dict]:
        """Extract text from an image file"""
        if not self.initialized:
            self.initialize()
        
        if not self.reader:
            return []
        
        try:
            if self.engine == "easyocr":
                results = self.reader.readtext(image_path)
                return [
                    {
                        'text': result[1],
                        'confidence': result[2],
                        'bbox': result[0]
                    }
                    for result in results
                ]
            elif self.engine == "paddleocr":
                results = self.reader.ocr(image_path, cls=True)
                extracted = []
                if results and results[0]:
                    for line in results[0]:
                        extracted.append({
                            'text': line[1][0],
                            'confidence': line[1][1],
                            'bbox': line[0]
                        })
                return extracted
        except Exception as e:
            print(f"OCR extraction error: {e}")
        
        return []
    
    def extract_text_from_bytes(self, image_bytes: bytes) -> List[Dict]:
        """Extract text from image bytes"""
        if not self.initialized:
            self.initialize()
        
        if not self.reader:
            return []
        
        try:
            import numpy as np
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
            
            if self.engine == "easyocr":
                results = self.reader.readtext(image_array)
                return [
                    {
                        'text': result[1],
                        'confidence': result[2],
                        'bbox': result[0]
                    }
                    for result in results
                ]
        except Exception as e:
            print(f"OCR bytes extraction error: {e}")
        
        return []
    
    def detect_ui_elements(self, image_path: str) -> Dict:
        """Detect UI elements like buttons, menus, panels"""
        text_regions = self.extract_text_from_image(image_path)
        
        ui_elements = {
            'buttons': [],
            'menus': [],
            'panels': [],
            'labels': [],
            'all_text': []
        }
        
        for region in text_regions:
            text = region['text'].strip()
            bbox = region['bbox']
            
            # Calculate dimensions
            if len(bbox) >= 2:
                width = abs(bbox[1][0] - bbox[0][0])
                height = abs(bbox[2][1] - bbox[0][1])
            else:
                width = height = 0
            
            element = {
                'text': text,
                'bbox': bbox,
                'confidence': region['confidence'],
                'width': width,
                'height': height
            }
            
            ui_elements['all_text'].append(element)
            
            # Classify UI elements based on text patterns
            if text in ['OK', 'Cancel', 'Apply', 'Save', 'Load', 'Delete', 'Add']:
                ui_elements['buttons'].append(element)
            elif text.endswith('...') or text in ['File', 'Edit', 'View', 'Render', 'Window', 'Help']:
                ui_elements['menus'].append(element)
            elif any(keyword in text for keyword in ['Panel', 'Properties', 'Outliner', 'Viewport']):
                ui_elements['panels'].append(element)
            else:
                ui_elements['labels'].append(element)
        
        return ui_elements
    
    def search_text_in_screen(self, image_path: str, search_term: str) -> List[Dict]:
        """Search for specific text in screen capture"""
        regions = self.extract_text_from_image(image_path)
        
        matches = []
        for region in regions:
            if search_term.lower() in region['text'].lower():
                matches.append(region)
        
        return matches
    
    def get_menu_structure(self, image_path: str) -> Optional[List[Dict]]:
        """Attempt to parse menu structure from screen"""
        ui_elements = self.detect_ui_elements(image_path)
        
        if not ui_elements['menus']:
            return None
        
        # Sort menus by position (top to bottom, left to right)
        sorted_menus = sorted(
            ui_elements['menus'],
            key=lambda x: (x['bbox'][0][1] if x['bbox'] else 0, x['bbox'][0][0] if x['bbox'] else 0)
        )
        
        return sorted_menus


class BlenderUIParser:
    """Specialized parser for Blender UI elements"""
    
    BLENDER_PANELS = [
        'Tool', 'Item', 'Transform', 'Object Properties',
        'Modifiers', 'Material Properties', 'Texture Properties',
        'Render Properties', 'Scene Properties', 'World Properties',
        'Camera Properties', 'Light Properties', 'Particle Properties',
        'Physics Properties', 'Constraint Properties'
    ]
    
    BLENDER_MODES = [
        'Object Mode', 'Edit Mode', 'Sculpt Mode', 'Vertex Paint',
        'Weight Paint', 'Texture Paint', 'Pose Mode', 'UV Editing',
        'Shading', 'Rendering', 'Compositing', 'Video Editing'
    ]
    
    def __init__(self, ocr_service: OCRService = None):
        self.ocr = ocr_service or OCRService()
    
    def detect_active_panel(self, image_path: str) -> Optional[str]:
        """Detect which Blender panel is currently active"""
        ui_elements = self.ocr.detect_ui_elements(image_path)
        
        for element in ui_elements['all_text']:
            text = element['text']
            for panel in self.BLENDER_PANELS:
                if panel.lower() in text.lower():
                    return panel
        
        return None
    
    def detect_current_mode(self, image_path: str) -> Optional[str]:
        """Detect current Blender mode"""
        ui_elements = self.ocr.detect_ui_elements(image_path)
        
        for element in ui_elements['all_text']:
            text = element['text']
            for mode in self.BLENDER_MODES:
                if mode.lower() in text.lower():
                    return mode
        
        return None
    
    def parse_modifier_stack(self, image_path: str) -> List[Dict]:
        """Parse modifier stack from screen"""
        ui_elements = self.ocr.detect_ui_elements(image_path)
        
        modifiers = []
        common_modifiers = [
            'Subdivision Surface', 'Mirror', 'Array', 'Boolean',
            'Solidify', 'Bevel', 'Decimate', 'Remesh', 'Wireframe'
        ]
        
        for element in ui_elements['all_text']:
            text = element['text']
            for mod in common_modifiers:
                if mod.lower() in text.lower():
                    modifiers.append({
                        'name': mod,
                        'detected_text': text,
                        'confidence': element['confidence']
                    })
                    break
        
        return modifiers
    
    def get_context_summary(self, image_path: str) -> Dict:
        """Get comprehensive context summary from screen"""
        return {
            'active_panel': self.detect_active_panel(image_path),
            'current_mode': self.detect_current_mode(image_path),
            'modifiers': self.parse_modifier_stack(image_path),
            'ui_elements': self.ocr.detect_ui_elements(image_path)
        }

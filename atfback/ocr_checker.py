from typing import List, Dict, Any
import tesseract 


class OCRChecker:
    """Validates and checks OCR data for alcohol beverage products."""
    
    @staticmethod
    def validate(
        images: List[bytes],
        brand_name: str,
        product_class: str,
        alcohol_content: str,
        net_contents: str,
        net_contents_unit: str
    ) -> tuple(Dict[str,bool], List[bytes]):
        
        valid_dict = {}
        valid_dict["brand"] = False
        valid_dict["class"] = False
        valid_dict["alcohol"] = False
        valid_dict["net"] = False
        valid_dict["warning"] = False
        
        # Image has to be rotated 3 times 90 degrees clockwise for processing
        # May still have issues with upside-down labels, but text is generally not diagonally aligned
        for image in images:
            
            
            
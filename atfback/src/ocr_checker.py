from pickletools import pystring
from typing import List, Dict, Any

import regex
import easyocr

import rtree
from thefuzz import fuzz
from PIL import Image
import cv2
from io import BytesIO
import numpy as np

#TODO Configuration file for OCR settings and thresholds
#TODO: Get bounding boxes for future matches
#TODO: Handle more edge cases in matching functions
#TODO: Handle multi-image submissions

class mockReader:
    def readtext(self, imagedata: bytes, rotation_info: List[int] = [0]):
        # Mock function to simulate OCR output
        return []
class OCRChecker:
    
    def __init__(self, modelSelect: str = 'easyocr'):
        self.modelname = modelSelect
        self.reader = easyocr.Reader(['en'], gpu=False, quantize=True, model_storage_directory="./EasyOCR", download_enabled=False)  
        #self.reader = mockReader()
        

    @staticmethod
    def clean_text(text: str) -> str:
        """Cleans the text by removing unwanted characters and normalizing whitespace.
        Args:
            text (str): string to clean

        Returns:
            str: string cleaned
        """
        # Remove unwanted characters (keep alphanumeric and basic punctuation)
        cleaned = regex.sub(r"[^a-zA-Z0-9\s\-%&]", '', text)  # Added '&' as a valid character
        # Normalize whitespace
        cleaned = regex.sub(r'\s+', ' ', cleaned).strip()
        return cleaned.upper()
        
    def validate(self,
            images,
            brand_name,
            product_class,
            alcohol_content,
            net_contents,
            net_contents_unit
        ):
        
        verifications = {
            'brand_name': False,
            'product_class': False,
            'alcohol_content': False,
            'net_contents': False,
            'gov_warn': False
        }
        boxes = {
            'brand_name': [],
            'product_class': [],
            'alcohol_content': [],
            'net_contents': [],
            'gov_warn': []
        }
        
        imagelen = len(images)
        i = 0
        while i < imagelen and not all(verifications.values()):
            imagedata = images[i]
            image = cv2.imdecode(np.frombuffer(imagedata, np.uint8), cv2.IMREAD_COLOR)
            height, width = image.shape[:2]
            
            ocrdata, rdix = self.process_image(imagedata)
            # no need to redo if it is found already
            if verifications['brand_name'] == False:
                verifications['brand_name'], boxes['brand_name'] = self.check_brand_name(ocrdata, rdix,width, height, brand_name)
            if verifications['product_class'] == False:
                verifications['product_class'], boxes['product_class'] = self.check_product_class(ocrdata, rdix, width, height, product_class)
            if verifications['alcohol_content'] == False:
                verifications['alcohol_content'], boxes['alcohol_content'] = self.check_alcohol_content(ocrdata, rdix, width, height, alcohol_content)
            if verifications['net_contents'] == False:
                verifications['net_contents'], boxes['net_contents'] = self.check_net_contents(ocrdata, rdix, width, height, net_contents, net_contents_unit)
            if verifications['gov_warn'] == False:
                verifications['gov_warn'], boxes['gov_warn'] = self.check_government_warning(ocrdata, rdix, width, height)    
            #TODO: do image rotations for better OCR if not all found

            i += 1 
        
        #TODO: Draw boxes on the images and return them for visualization
        # for now, just return the original images
        
        oimages = images
        
        return verifications, oimages
    
    def process_image (self, imagedata: bytes):
        """_summary_

        Args:
            imagedata (bytes): The image

        Raises:
            ValueError: _description_
            
        Returns:
            ocrdata (Dict[int, dict[str, Any]]): OCR data with rdix ids as keys
            rdix (rtree.index.Index): rtree index of bounding boxes
        """
        
        
        #get image dimensions
        

        #Holds found text, confidence, bounding box. uses an id
        ocrdata : Dict[int, dict[str, Any]] = {}
        rdix : rtree.index.Index
        match self.modelname:
            case 'easyocr':
                ocrdata, rdix = self.get_easy_data(imagedata)
            case '_':
                raise ValueError(f"Unsupported OCR model: {self.modelname}")        
        return ocrdata, rdix


    def check_government_warning(self, ocrdata: Dict[int, dict[str, Any]], rdix: rtree.index.Index, width: int, height: int) -> bool:
        """Checks for government warning in the text. Tends to be in all caps and words are together. Simple to just look for the phrase.

        Args:
            ocrdata (Dict[int, dict[str, Any]]): OCR data with rdix ids as keys
            rdix (rtree.index.Index): rtree index of bounding boxes

        Returns:
            bool: True if present, false if not
            list: list of bounding boxes for the found text
        """
        ocr_texts = [entry['text'].upper() for entry in ocrdata.values()]
        for text in ocr_texts:
            if len(text) > 10 and fuzz.partial_ratio("GOVERNMENT WARNING", text.upper()) > 80:
                return True, []
        return False, []

    def check_brand_name(self, ocrdata: Dict[int, dict[str, Any]], rdix: rtree.index.Index, width: int, height: int, brand_name: str) -> bool:
        """Checks for brand name in the text

        Args:
            ocrdata (Dict[int, dict[str, Any]]): OCR data with rdix ids as keys
            rdix (rtree.index.Index): rtree index of bounding boxes
            brand_name (str): brand name to check

        Returns:
            bool: True if present, false if not
        """
        # Brand name is generally in bigger text, but may be split across boxes. Also may have OCR errors due to 'fancy' fonts
        for i in ocrdata.keys():
            ctext = self.clean_text(ocrdata[i]['text'])
            cid = ocrdata[i]
            if fuzz.ratio(brand_name.upper(), ctext) > 75 or (len(ctext) > len(brand_name) and fuzz.partial_ratio(brand_name.upper(), ctext) > 85):
                return True, []
        ## TODO: check for split text boxes
        return False, []

    def check_product_class(self, ocrdata: Dict[int, dict[str, Any]], rdix: rtree.index.Index, width: int, height: int, product_class: str) -> bool:
        """Checks for product class in the text

        Args:
            ocrdata (Dict[int, dict[str, Any]]): OCR data with rdix ids as keys
            rdix (rtree.index.Index): rtree index of bounding boxes
            product_class (str): product class to check

        Returns:
            bool: True if present, false if not
            list: list of bounding boxes for the found text
        """
        # Product class should be in close proximity to brand name, usually below it; multiple words should be close together
        
        for i in ocrdata.keys():
            ctext = self.clean_text(ocrdata[i]['text'])
            cid = ocrdata[i]
            if fuzz.ratio(product_class.upper(), ctext) > 75 or (len(ctext) > len(product_class) and fuzz.partial_ratio(product_class.upper(), ctext) > 85):
                return True, []
        ## TODO: check for split text boxes
        return False, []

    def check_alcohol_content(self, ocrdata: Dict[int, dict[str, Any]], rdix: rtree.index.Index, width: int, height: int, alcohol_content: str) -> bool:
        """Checks for alcohol content in the text
        Alcohol/Alc may be before it or after it. By Volume is always after both. Ideally it's in one string, but may be in multiple boxes

        Args:
            ocrdata (Dict[int, dict[str, Any]]): OCR data with rdix ids as keys
            rdix (rtree.index.Index): rtree index of bounding boxes
            alcohol_content (str): alcohol content to check

        Returns:
            bool: True if present, false if not
            list: list of bounding boxes for the found text
        """
        #Must account for different formats of alcohol content
        # e.g., "40% Alcohol by Volume", "40% Alc by Vol", "Alcohol 40% by Volume", Alc 40% by Vol and 40% Alc/Vol among others"
        # regex would be ideal, but fuzzy matching may be more reliable given OCR errors
        # this means all variations must be generated and checked to utilize fuzzy matching
        abvlist = [  f"{alcohol_content}% ALCOHOL BY VOLUME",
                                f"{alcohol_content}% ALC BY VOLUME",
                                f"{alcohol_content}% ALCOHOL BY VOL",
                                f"{alcohol_content}% ALC BY VOL",
                                f"{alcohol_content}% ALC/VOL",
                                f"ALCOHOL {alcohol_content}% BY VOLUME",
                                f"ALC {alcohol_content}% BY VOLUME",
                                f"ALCOHOL {alcohol_content}% BY VOL",
                                f"ALC {alcohol_content}% BY VOL"]

        #would be 'faster' to search boxes by the alcohol_content and then look for the rest, but fuzzy matching may be inaccurate that way
        for i in ocrdata.keys():
            ctext = self.clean_text(ocrdata[i]['text'])
            cid = ocrdata[i]
            for abvformat in abvlist:
                if fuzz.ratio(abvformat, ctext) > 75 or (len(ctext) > len(abvformat) and fuzz.partial_ratio(abvformat, ctext) > 75):
                    #now that the larger text is 'close enough', verify the alcohol content number is close enough
                    if fuzz.ratio(alcohol_content.upper(), ctext) > 80 or (len(ctext) > len(alcohol_content) and fuzz.partial_ratio(alcohol_content.upper(), ctext) > 85):
                        return True, []
                    return False, []
        #TODO: find alcohol by volume in split boxes from the number
        return False, []

    def check_net_contents(self, ocrdata: Dict[int, dict[str, Any]], rdix: rtree.index.Index, width: int, height: int, net_contents: str, net_contents_unit: str) -> bool:
        """Checks for net contents in the text
        Text should be close together and not in abstracted locations
        Args:
            ocrdata (Dict[int, dict[str, Any]]): OCR data with rdix ids as keys
            rdix (rtree.index.Index): rtree index of bounding boxes
            net_contents (str): net contents to check
            net_contents_unit (str): net contents unit to check

        Returns:
            bool: True if present, false if not
            list: list of bounding boxes for the found text
        """
        if net_contents_unit == 'L':
            # Check for liter/liters. Unit must account for L, Liter, Liters
            if net_contents == '1':
                fullnet = f"{net_contents} LITER".strip().upper()
            else:
                fullnet = f"{net_contents} LITERS".strip().upper()
            for i in ocrdata.keys():
                ctext = self.clean_text(ocrdata[i]['text'])
                cid = ocrdata[i]
                if fuzz.ratio(fullnet, ctext) > 78 or (len(ctext) > len(fullnet) and fuzz.partial_ratio(fullnet, ctext) > 85):
                    #if match is found, do a fuzz check on the possible number only. First elements should be the number
                    #get first token (up to first space
                    tokens = ctext.split(' ')
                    if len(tokens) > 0:
                        numtoken = tokens[0]
                        if fuzz.ratio(net_contents.upper(), numtoken) > 80):
                            return True, [cid]
                    
                    return True, []
            ##TODO: check for split text and use of L instead of Liters
            return False, []

        ## big enough for a large match
        if net_contents_unit == 'fl oz':
            fullnet = f"{net_contents} {net_contents_unit}".strip().upper()
            for i in ocrdata.keys():
                ctext = self.clean_text(ocrdata[i]['text'])
                cid = ocrdata[i]
                if fuzz.ratio(fullnet, ctext) > 78:
                    return True, []
                # TODO: Check nearby boxes for split text when dealing with ml and L; more straight forward with fl oz
            return False, []
                
        if net_contents_unit == 'ml':
            # Check for milliliters
            fullnet = f"{net_contents} {net_contents_unit}".strip().upper()
            for i in ocrdata.keys():
                ctext = self.clean_text(ocrdata[i]['text'])
                cid = ocrdata[i]
                ## direct match, use ratio; for a larger grab use partial ratio
                if fuzz.ratio(fullnet, ctext) > 78 or (len(ctext) > len(fullnet) and fuzz.partial_ratio(fullnet, ctext) > 85):
                    return True, []
            #if no full can be found, check for split
            #TODO: implement split check
            return False, []
        pass

    def get_easy_data(self, imagedata: bytes) -> List[Dict[str, Any]]:
        reader = self.reader
        result = reader.readtext(imagedata, workers=2, rotation_info=[0,90,270])
        out = {}
        ridx = rtree.index.Index()
        bbid_counter = 0
        text=""
        for (bbox, text, prob) in result:
            verts = [{"x": int(v[0]), "y": int(v[1])} for v in bbox]
            minx = min(v[0] for v in bbox)
            miny = min(v[1] for v in bbox)
            maxx = max(v[0] for v in bbox)
            maxy = max(v[1] for v in bbox)
            ridx.insert(bbid_counter, (minx, miny, maxx, maxy))
            finding = {
                "text": text,
                "confidence": round(float(prob), 4),
                "bbox": verts
            }
            out[bbid_counter] = finding
            bbid_counter += 1
            
        return out, ridx
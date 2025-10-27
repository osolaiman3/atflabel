"""
Test suite for OCRChecker class
Tests process_image and individual validation methods using pytest
"""
from turtle import width
import cv2
import pytest
import os
import numpy as np

from src.ocr_checker import OCRChecker
from pathlib import Path


@pytest.fixture(scope="module")
def test_image_data():
    """Load test image once for all tests"""
    #test_image_path = Path(__file__).parent.parent.parent / "examples" / "GreyGoose.jpg"
    test_image_path = Path(__file__).parent.parent.parent / "examples" / "2white christmas.png"
    #test_image_path = Path(__file__).parent.parent.parent / "examples" / "rotright.jpg"
    # test_image_path = Path(__file__).parent.parent.parent / "examples" / "rotleft.jpg"
    
    if not test_image_path.exists():
        pytest.skip(f"Test image not found at {test_image_path}")
    
    with open(test_image_path, 'rb') as f:
        return f.read()


@pytest.fixture(scope="module")
def ocr_checker():
    """Create OCRChecker instance"""
    return OCRChecker(modelSelect='easyocr')


@pytest.fixture(scope="module")
def processed_image(test_image_data, ocr_checker):
    """Process image once and reuse for all tests"""
    ocrdata, rdix  = ocr_checker.process_image(test_image_data)
    
    
    
    width, height = None, None
    image_size = cv2.imdecode(np.frombuffer(test_image_data, np.uint8), cv2.IMREAD_COLOR).shape
    if image_size is not None:
        height, width = image_size[:2]
        print("Image dimensions:", width, height)

    return ocrdata, rdix, width, height



class TestProcessImage:
    """Tests for process_image method"""
    
    def test_returns_dict_and_index(self, processed_image):
        """Test that process_image returns ocrdata dict and rtree index"""
        ocrdata, rdix, width, height = processed_image
        assert isinstance(ocrdata, dict), "ocrdata should be a dict"
        assert rdix is not None, "rdix should not be None"
        assert isinstance(width, int), "width should be int"
        assert isinstance(height, int), "height should be int"
    
    def test_ocrdata_structure(self, processed_image):
        """Test that ocrdata has correct structure"""
        ocrdata, _, _, _ = processed_image
        assert len(ocrdata) > 0, "Should detect at least one text element"
        
        # Check structure of first entry
        first_entry = next(iter(ocrdata.values()))
        assert 'text' in first_entry, "Entry should have 'text' field"
        assert 'confidence' in first_entry, "Entry should have 'confidence' field"
        assert 'bbox' in first_entry, "Entry should have 'bbox' field"
    
    def test_rtree_index_populated(self, processed_image):
        """Test that rtree index contains bounding boxes"""
        ocrdata, rdix, _, _ = processed_image
        # Query the entire space to count indexed boxes
        count = len(list(rdix.intersection((-float('inf'), -float('inf'), float('inf'), float('inf')))))
        assert count == len(ocrdata), "Rtree should contain same number of boxes as ocrdata"


class TestBrandName:
    """Tests for check_brand_name method"""
    
    @pytest.mark.parametrize("brand_name,expected", [
        ("Grey Goose", False),  
        ("Jack Daniels", False), 
        ("Budweiser", False),
        ("Samuel Adams", True), 
        ("", True)
        ])         
    def test_brand_detection(self, processed_image, ocr_checker, brand_name, expected):
        """Test brand name detection with various inputs"""
        ocrdata, rdix, width, height = processed_image
        found, boxes = ocr_checker.check_brand_name(ocrdata, rdix, width, height, brand_name)
        # Skip assertion if method not implemented
        if found is None:
            pytest.skip("check_brand_name not implemented")
        print(f"Brand name '{brand_name}' found: {found}, boxes: {boxes}")
        print(ocrdata)
        assert isinstance(found, bool), "Should return boolean"
        assert isinstance(boxes, list), "Should return list of boxes"


class TestProductClass:
    """Tests for check_product_class method"""
    
    @pytest.mark.parametrize("product_class", [
        "Tennessee Whiskey",
        "Vodka",
        "Bourbon",
        "Beer",
        "Wine"
    ])
    def test_product_class_detection(self, processed_image, ocr_checker, product_class):
        """Test product class detection"""
        ocrdata, rdix, width, height = processed_image
        found, boxes = ocr_checker.check_product_class(ocrdata, rdix, width, height, product_class)
        if found is None:
            pytest.skip("check_product_class not implemented")
        print(f"Product class '{product_class}' found: {found}, boxes: {boxes}")
        assert isinstance(found, bool), "Should return boolean"
        assert isinstance(boxes, list), "Should return list of boxes"


class TestAlcoholContent:
    """Tests for check_alcohol_content method"""
    
    @pytest.mark.parametrize("alcohol_content", [
        "40",
        "5",
        "12.5",
        "13.5",
        "7.5"
    ])
    def test_alcohol_detection(self, processed_image, ocr_checker, alcohol_content):
        """Test alcohol content detection"""
        ocrdata, rdix, width, height = processed_image
        found, boxes = ocr_checker.check_alcohol_content(ocrdata, rdix, width, height, alcohol_content)
        if found is None:
            pytest.skip("check_alcohol_content not implemented")
        print(f"Alcohol content {alcohol_content}% found: {found}, boxes: {boxes}")
        assert isinstance(found, bool), "Should return boolean"
        assert isinstance(boxes, list), "Should return list of boxes"


class TestNetContents:
    """Tests for check_net_contents method"""
    
    @pytest.mark.parametrize("amount,unit", [
        ("750", "ml"),
        ("1", "L"),
        ("12", "fl oz"),
        ("355", "ml")
    ])
    def test_net_contents_detection(self, processed_image, ocr_checker, amount, unit):
        """Test net contents detection"""
        ocrdata, rdix, width, height = processed_image
        found, boxes = ocr_checker.check_net_contents(ocrdata, rdix, width, height, amount, unit)
        if found is None:
            pytest.skip("check_net_contents not implemented")
        print(f"Net contents {amount} {unit} found: {found}, boxes: {boxes}")
        assert isinstance(found, bool), "Should return boolean"
        assert isinstance(boxes, list), "Should return list of boxes"


class TestGovernmentWarning:
    """Tests for check_government_warning method"""
    
    def test_warning_detection(self, processed_image, ocr_checker):
        """Test government warning detection"""
        ocrdata, rdix, width, height = processed_image
        found, boxes = ocr_checker.check_government_warning(ocrdata, rdix, width, height)
        print(f"Government warning found: {found}, boxes: {boxes}")
        
        assert isinstance(found, bool), "Should return boolean"
        assert isinstance(boxes, list), "Should return list of boxes"


class TestFullValidation:
    """Tests for complete validate method"""
    
    def test_validate_returns_dict(self, test_image_data, ocr_checker):
        """Test that validate returns proper dictionary"""
        result = ocr_checker.validate(
            images=[test_image_data],
            brand_name="Jack Daniels",
            product_class="Tennessee Whiskey",
            alcohol_content="40",
            net_contents="750",
            net_contents_unit="ml"
        )
        
        if result is None:
            pytest.skip("validate not fully implemented")
        
        assert isinstance(result, (dict, tuple)), "validate should return dict or tuple"
    
    def test_validate_checks_all_fields(self, test_image_data, ocr_checker):
        """Test that validate checks all required fields"""
        result = ocr_checker.validate(
            images=[test_image_data],
            brand_name="Test Brand",
            product_class="Test Class",
            alcohol_content="10",
            net_contents="500",
            net_contents_unit="ml"
        )
        
        if result is None:
            pytest.skip("validate not fully implemented")
        
        # Extract validations dict from result
        if isinstance(result, tuple):
            validations = result[0]
        else:
            validations = result
        
        expected_keys = ['brand_name', 'product_class', 'alcohol_content', 'net_contents', 'gov_warn']
        for key in expected_keys:
            assert key in validations, f"validate should check {key}"

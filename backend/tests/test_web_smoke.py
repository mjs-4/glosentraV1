#!/usr/bin/env python3
"""
Glosentra Web Application Smoke Tests
Basic functionality tests to ensure the application is working correctly
"""

import pytest
import requests
import json
import io
from PIL import Image
import sys
from pathlib import Path


def add_project_root_to_path():
    """Add project root to Python path."""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))


class TestGlosentraWeb:
    """Test class for Glosentra web application."""
    
    @classmethod
    def setup_class(cls):
        """Setup test class."""
        add_project_root_to_path()
        cls.base_url = "http://localhost:5000"
        cls.api_url = f"{cls.base_url}/api"
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = requests.get(f"{self.api_url}/healthz", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True
        print("✓ Health check passed")
    
    def test_home_page(self):
        """Test home page loads correctly."""
        response = requests.get(self.base_url, timeout=10)
        assert response.status_code == 200
        
        # Check for key content
        content = response.text
        assert "Glosentra" in content
        assert "Advanced Computer Vision" in content
        assert "Object Detection" in content
        print("✓ Home page loads correctly")
    
    def test_models_endpoint(self):
        """Test models endpoint."""
        response = requests.get(f"{self.api_url}/models", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "models" in data
        
        # Check for expected model types
        models = data["models"]
        expected_tasks = ["detect", "segment", "classify", "pose"]
        for task in expected_tasks:
            assert task in models
            assert "path" in models[task]
            assert "loaded" in models[task]
        print("✓ Models endpoint working")
    
    def test_process_image_detection(self):
        """Test image processing with object detection."""
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='black')
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        # Prepare form data
        files = {'image': ('test.jpg', img_byte_arr, 'image/jpeg')}
        data = {'model_type': 'detect'}
        
        # Send request
        response = requests.post(
            f"{self.api_url}/process",
            files=files,
            data=data,
            timeout=30
        )
        
        assert response.status_code == 200
        
        result = response.json()
        assert "success" in result
        assert "predictions" in result
        assert "timing" in result
        
        if result["success"]:
            assert "boxes" in result["predictions"]
            assert "classes" in result["predictions"]
            assert "confidences" in result["predictions"]
            
            # Check timing data
            timing = result["timing"]
            assert "inference_ms" in timing
            assert "total_ms" in timing
            assert "fps" in timing
            
            print("✓ Image processing (detection) working")
        else:
            print(f"⚠️ Image processing returned error: {result.get('error', 'Unknown error')}")
    
    def test_process_image_classification(self):
        """Test image processing with classification."""
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='black')
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        # Prepare form data
        files = {'image': ('test.jpg', img_byte_arr, 'image/jpeg')}
        data = {'model_type': 'classify'}
        
        # Send request
        response = requests.post(
            f"{self.api_url}/process",
            files=files,
            data=data,
            timeout=30
        )
        
        assert response.status_code == 200
        
        result = response.json()
        assert "success" in result
        assert "predictions" in result
        assert "timing" in result
        
        if result["success"]:
            # Classification should have predictions array
            assert "predictions" in result["predictions"]
            print("✓ Image processing (classification) working")
        else:
            print(f"⚠️ Image processing returned error: {result.get('error', 'Unknown error')}")
    
    def test_invalid_file_type(self):
        """Test handling of invalid file types."""
        # Create a text file instead of image
        files = {'image': ('test.txt', b'not an image', 'text/plain')}
        data = {'model_type': 'detect'}
        
        response = requests.post(
            f"{self.api_url}/process",
            files=files,
            data=data,
            timeout=10
        )
        
        # Should handle gracefully (either 400 or 200 with error)
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False
            assert "error" in result
            print("✓ Invalid file type handled gracefully")
        else:
            print("✓ Invalid file type rejected with 400")
    
    def test_missing_file(self):
        """Test handling of missing file."""
        data = {'model_type': 'detect'}
        
        response = requests.post(
            f"{self.api_url}/process",
            data=data,
            timeout=10
        )
        
        assert response.status_code == 400
        
        result = response.json()
        assert result["success"] is False
        assert "No image file provided" in result["error"]
        print("✓ Missing file handled correctly")
    
    def test_invalid_model_type(self):
        """Test handling of invalid model type."""
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='black')
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        # Prepare form data with invalid model type
        files = {'image': ('test.jpg', img_byte_arr, 'image/jpeg')}
        data = {'model_type': 'invalid'}
        
        response = requests.post(
            f"{self.api_url}/process",
            files=files,
            data=data,
            timeout=10
        )
        
        assert response.status_code == 400
        
        result = response.json()
        assert result["success"] is False
        assert "Invalid model type" in result["error"]
        print("✓ Invalid model type handled correctly")
    
    def test_page_endpoints(self):
        """Test that all page endpoints return 200."""
        endpoints = [
            "/",
            "/deploy/detect",
            "/deploy/segment", 
            "/deploy/classify",
            "/deploy/pose",
            "/realtime",
            "/analytics",
            "/docs",
            "/finetune",
            "/about"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"
            assert "Glosentra" in response.text, f"Endpoint {endpoint} missing title"
        
        print("✓ All page endpoints working")
    
    def test_analytics_endpoint(self):
        """Test analytics endpoint."""
        response = requests.get(f"{self.api_url}/analytics/stats", timeout=10)
        assert response.status_code in [200, 400]  # 400 if analytics disabled
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            print("✓ Analytics endpoint working")
        else:
            print("✓ Analytics endpoint correctly disabled")


def run_smoke_tests():
    """Run all smoke tests."""
    print("🧪 Running Glosentra Smoke Tests")
    print("="*50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/api/healthz", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Please start the server first:")
            print("python scripts/run_dev.py")
            return False
    except requests.exceptions.RequestException:
        print("❌ Server not running. Please start the server first:")
        print("python scripts/run_dev.py")
        return False
    
    print("✓ Server is running")
    
    # Run tests
    test_instance = TestGlosentraWeb()
    test_instance.setup_class()
    
    tests = [
        test_instance.test_health_check,
        test_instance.test_home_page,
        test_instance.test_models_endpoint,
        test_instance.test_page_endpoints,
        test_instance.test_analytics_endpoint,
        test_instance.test_process_image_detection,
        test_instance.test_process_image_classification,
        test_instance.test_invalid_file_type,
        test_instance.test_missing_file,
        test_instance.test_invalid_model_type,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All smoke tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)

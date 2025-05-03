from locust import HttpUser, task, between
import base64
import os
from test_base_64 import *

class ImageComparisonLoadTest(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load test images once during initialization
        self.image1_base64 = self._load_test_image("")
        self.image2_base64 = self._load_test_image("")
    
    def _load_test_image(self, image_name):
        """Helper method to load and encode test images"""
        try:
            with open(image_name, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            # Fallback to a small dummy base64 string if test images don't exist
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    
    @task
    def compare_images(self):
        """Main task for image comparison load testing"""
        payload = {
            "image1": self.image1_base64,
            "image2": self.image2_base64
        }
        
        with self.client.post(
            "/compare",  # Update this endpoint path according to your API
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")
from locust import HttpUser, task, between  # Import Locust classes for load testing
import base64  # Standard library for encoding binary data
from test_base_64 import *  # Import helpers or constants from external test module

class ImageComparisonLoadTest(HttpUser):
    wait_time = between(1, 3)  # Simulate user wait time between requests (1–3 seconds)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preload base64-encoded images on user start
        self.image1_base64 = self._load_test_image("")
        self.image2_base64 = self._load_test_image("")
    
    def _load_test_image(self, image_name):
        """Load image from file and encode it as base64"""
        try:
            with open(image_name, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')  # Convert binary to base64 string
        except FileNotFoundError:
            # Use fallback base64 string if image file is missing
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    
    @task
    def compare_images(self):
        """Send image comparison request to the API"""
        payload = {
            "image1": self.image1_base64,  # First base64-encoded image
            "image2": self.image2_base64   # Second base64-encoded image
        }
        
        with self.client.post(
            "/compare",  # Target API endpoint for image comparison
            json=payload,
            catch_response=True  # Capture response to mark success/failure
        ) as response:
            if response.status_code == 200:
                response.success()  # Mark as successful if response is OK
            else:
                response.failure(f"Failed with status code: {response.status_code}")  # Mark as failed otherwise

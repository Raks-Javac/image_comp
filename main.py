import base64
import os
from typing import List
from fastapi import FastAPI, HTTPException, Response, Request
from models.image_models import ImageComparisonRequest, ImageComparisonResponse
from dotenv import load_dotenv
import google.generativeai as genai
import io
from PIL import Image
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
import cachetools  # Add this import

# Load environment variables
load_dotenv()

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# Add these imports at the top
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI(title="Image Comparison API", debug=True)

# Add GZIP compression for better performance with large payloads
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CORS middleware with more specific configuration for load testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create an LRU cache for image comparison results
# Cache size of 100 items with 5 minute TTL
comparison_cache = cachetools.TTLCache(maxsize=100, ttl=300)

def get_cache_key(image1: str, image2: str) -> str:
    """Generate a cache key from the two image strings"""
    return f"{hash(image1)}-{hash(image2)}"

def decode_base64_to_image(base64_string: str) -> Image.Image:
    try:
        # Remove data URL prefix if present
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        
        # Add input validation for base64 string
        if not base64_string or len(base64_string) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Invalid image size")
            
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # Optimize image for processing
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # Resize large images to reduce processing time
        max_size = 1024
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Image Comparison API is running"}

@app.post("/compare", response_model=ImageComparisonResponse)
async def compare_images(request: ImageComparisonRequest, response: Response):
    try:
        # Add logging for debugging
        logger.debug("Received image comparison request")
        
        # Check cache first
        cache_key = get_cache_key(request.image1, request.image2)
        if cache_key in comparison_cache:
            logger.debug("Cache hit")
            response.headers["X-Cache"] = "HIT"
            return comparison_cache[cache_key]
            
        logger.debug("Cache miss")
        response.headers["X-Cache"] = "MISS"
        
        # Decode base64 images
        image1 = decode_base64_to_image(request.image1)
        image2 = decode_base64_to_image(request.image2)
        
        # Prepare prompt for Gemini
        prompt = """
        Compare these two images and provide:
        1. A similarity score from 0 to 100, where 0 means completely different and 100 means identical
        2. A brief explanation of the similarities and differences
        
        Format your response exactly like this:
        Score: [number]
        Explanation: [your explanation]
        """
        
        # Generate response from Gemini with timeout
        response = model.generate_content([prompt, image1, image2])
        response_text = response.text
        
        # Parse the response
        lines = response_text.strip().split('\n')
        score_line = next((line for line in lines if line.startswith("Score:")), None)
        
        if not score_line:
            result = {"similarity_score": 50, "explanation": "Could not parse score. " + response_text}
        else:
            try:
                score = float(score_line.replace("Score:", "").strip())
                score = max(0, min(100, score))
                
                explanation_index = lines.index(score_line) + 1 if score_line in lines else 0
                explanation = "\n".join(lines[explanation_index:])
                explanation = explanation.replace("Explanation:", "").strip()
                
                result = {"similarity_score": score, "explanation": explanation}
            except ValueError:
                result = {"similarity_score": 50, "explanation": "Score parsing failed. " + response_text}
        
        # Cache the result
        comparison_cache[cache_key] = result
        return result
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Modify the main block for better debugging
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        debug=True,
        log_level="debug",
        workers=1  # Use single worker for debugging
    )
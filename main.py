import base64
import os
from typing import List
from fastapi import FastAPI, HTTPException
from models.image_models import ImageComparisonRequest, ImageComparisonResponse
from dotenv import load_dotenv
import google.generativeai as genai
import io
from PIL import Image

# Load environment variables
load_dotenv()

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

app = FastAPI(title="Image Comparison API")



def decode_base64_to_image(base64_string: str) -> Image.Image:
    try:
        # Remove data URL prefix if present
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Image Comparison API is running"}

@app.post("/compare", response_model=ImageComparisonResponse)
async def compare_images(request: ImageComparisonRequest):
    try:
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
        
        # Generate response from Gemini
        response = model.generate_content([prompt, image1, image2])
        response_text = response.text
        
        # Parse the response
        lines = response_text.strip().split('\n')
        score_line = next((line for line in lines if line.startswith("Score:")), None)
        
        if not score_line:
            return {"similarity_score": 50, "explanation": "Could not parse score. " + response_text}
        
        try:
            score = float(score_line.replace("Score:", "").strip())
            # Ensure score is between 0 and 100
            score = max(0, min(100, score))
        except ValueError:
            score = 50  # Default if parsing fails
        
        # Extract explanation (everything after the score line)
        explanation_index = lines.index(score_line) + 1 if score_line in lines else 0
        explanation = "\n".join(lines[explanation_index:])
        explanation = explanation.replace("Explanation:", "").strip()
        
        return {"similarity_score": score, "explanation": explanation}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
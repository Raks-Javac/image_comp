from typing import List
from pydantic import BaseModel
class ImageComparisonRequest(BaseModel):
    image1: str  # base64 encoded image
    image2: str  # base64 encoded image

class ImageComparisonResponse(BaseModel):
    similarity_score: float
    explanation: str




import datetime

from pydantic import BaseModel
class ImageComparisonRequest(BaseModel):
    image1: str  # base64 encoded image
    image2: str  # base64 encoded image

class ImageComparisonResponse(BaseModel):
    similarity_score: float
    explanation: str
    status: str = "success"
    message: str = "Comparison successful"
    timestamp: str = datetime.datetime.now().isoformat()
    data: dict | None = {}
    




class GeneralReponse:
    def __init__(self, status: str, message: str, data: any = None, timestamp: str = None):
        self.status = status
        self.message = message
        self.data = data
        self.timestamp = timestamp if timestamp else datetime.datetime.now().isoformat()
    
    def __dict__(self):
        
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp
        }
from pydantic import BaseModel, Field, validator
from typing import Optional

class PredictionRequest(BaseModel):
    frame: str
    frame_id: int = Field(ge=0)
    timestamp: float
    
    @validator('frame')
    def validate_frame(cls, v):
        if not v or len(v) < 100:
            raise ValueError('Invalid frame data')
        return v

class PredictionData(BaseModel):
    text: Optional[str]
    confidence: float
    gesture_id: Optional[str]

class MetadataInfo(BaseModel):
    landmarks_detected: bool
    processing_time_ms: Optional[float] = None
    model_version: str = "v1.0-mock"
    warning: Optional[str] = None

class ErrorInfo(BaseModel):
    code: str
    message: str

class PredictionResponse(BaseModel):
    success: bool
    frame_id: int
    prediction: Optional[PredictionData]
    metadata: MetadataInfo
    error: Optional[ErrorInfo] = None

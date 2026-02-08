# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import cv2
import numpy as np

# Import the new Ensemble Loader
from models.gesture_model import get_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model on startup
model = get_model()

class ImageRequest(BaseModel):
    image: str  # base64 string

@app.post("/api/predict")
def predict(req: ImageRequest):
    try:
        # 1. Decode base64
        if "," in req.image:
            image_data = req.image.split(",")[1]
        else:
            image_data = req.image

        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)

        # 2. Decode to OpenCV Frame (BGR)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # 3. Predict using Ensemble
        gesture, confidence = model.predict(frame)

        return {
            "gesture": gesture,
            "confidence": confidence,
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {"gesture": "Error", "confidence": 0.0}

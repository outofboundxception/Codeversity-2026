from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import cv2
import numpy as np

from models.gesture_model import get_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = get_model()


class ImageRequest(BaseModel):
    image: str  # base64 string


@app.post("/api/predict")
def predict(req: ImageRequest):
    # 🔹 Decode base64
    image_data = req.image.split(",")[1]
    image_bytes = base64.b64decode(image_data)

    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    gesture, confidence = model.predict(frame)

    return {
        "gesture": gesture,
        "confidence": confidence,
    }

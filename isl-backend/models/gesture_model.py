import numpy as np
from typing import Tuple
import random

class MockGestureModel:
    def __init__(self):
        self.gestures = ["Hello", "Thank you", "Please", "Yes", "No", "Help", "Sorry", "Welcome", "Goodbye", "How are you"]
        self.model_version = "v1.0-mock"
        print("🤖 Mock gesture model loaded")
    
    def predict(self, landmarks: np.ndarray) -> Tuple[str, float]:
        if landmarks.shape != (21, 3):
            raise ValueError(f"Expected landmarks shape (21, 3), got {landmarks.shape}")
        palm_center_y = np.mean(landmarks[:, 1])
        if palm_center_y < 0.3:
            gesture = "Hello"
            confidence = 0.92
        elif palm_center_y < 0.5:
            gesture = "Thank you"
            confidence = 0.87
        elif palm_center_y < 0.7:
            gesture = "Please"
            confidence = 0.81
        else:
            gesture = random.choice(self.gestures)
            confidence = random.uniform(0.65, 0.95)
        return gesture, round(confidence, 2)
    
    def get_info(self) -> dict:
        return {
            "model_type": "Mock ISL Recognizer",
            "version": self.model_version,
            "supported_gestures": len(self.gestures),
            "input_shape": "(21, 3)"
        }

_model_instance = None

def get_model() -> MockGestureModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = MockGestureModel()
    return _model_instance

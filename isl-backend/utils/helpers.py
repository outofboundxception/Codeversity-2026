import base64
import numpy as np
from PIL import Image
from io import BytesIO
import cv2

def decode_base64_image(base64_string: str) -> np.ndarray:
    try:
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_bytes))
        image_np = np.array(image)
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        return image_np
    except Exception as e:
        raise ValueError(f"Failed to decode image: {str(e)}")

def preprocess_frame(frame: np.ndarray, target_size=(640, 480)) -> np.ndarray:
    if frame.shape[1] != target_size[0] or frame.shape[0] != target_size[1]:
        frame = cv2.resize(frame, target_size)
    return frame

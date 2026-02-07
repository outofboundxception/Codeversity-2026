import torch
import torch.nn.functional as F
import torchvision.models as models
import cv2
import numpy as np


class ISLGestureModel:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 🔹 Load checkpoint
        checkpoint = torch.load(
            "indian_mnv2_best.pt",
            map_location=self.device
        )

        # 🔹 Extract metadata from checkpoint
        raw_label_map = checkpoint["label_map"]   # label -> index
        self.img_size = checkpoint.get("img_size", 224)
        self.grayscale = checkpoint.get("grayscale", False)

        # 🔹 INVERT label map: index -> label (THIS FIXES YOUR BUG)
        self.idx_to_label = {v: k for k, v in raw_label_map.items()}
        num_classes = len(self.idx_to_label)

        # 🔹 Build MobileNetV2 architecture
        self.model = models.mobilenet_v2(weights=None)
        self.model.classifier[1] = torch.nn.Linear(
            self.model.classifier[1].in_features,
            num_classes
        )

        # 🔹 Load trained weights
        self.model.load_state_dict(checkpoint["model_state"])
        self.model.to(self.device)
        self.model.eval()

        print("🔥 ISL model loaded correctly")
        print(f"Classes ({num_classes}): {self.idx_to_label}")
        print(f"Image size: {self.img_size}, Grayscale: {self.grayscale}")

    def preprocess(self, frame: np.ndarray) -> torch.Tensor:
        # Resize
        frame = cv2.resize(frame, (self.img_size, self.img_size))

        # Optional grayscale
        if self.grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = np.expand_dims(frame, axis=-1)

        # BGR -> RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Normalize
        frame = frame.astype(np.float32) / 255.0

        # HWC -> CHW
        frame = np.transpose(frame, (2, 0, 1))

        # Add batch dimension
        tensor = torch.tensor(frame).unsqueeze(0)

        return tensor.to(self.device)

    def predict(self, frame: np.ndarray):
        if frame is None:
            return "No frame", 0.0

        x = self.preprocess(frame)

        with torch.no_grad():
            logits = self.model(x)
            probs = F.softmax(logits, dim=1)

        confidence, idx = torch.max(probs, dim=1)

        # 🔹 SAFE lookup (no KeyError)
        label = self.idx_to_label.get(idx.item(), "Unknown")
        return label, round(confidence.item(), 2)


# 🔹 Singleton instance (FastAPI-safe)
_model_instance = None

def get_model():
    global _model_instance
    if _model_instance is None:
        _model_instance = ISLGestureModel()
    return _model_instance

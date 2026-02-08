# models/gesture_model.py
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.transforms import InterpolationMode
from PIL import Image
import cv2
import numpy as np
import json
from pathlib import Path

# ================= CONFIG (From 3_webcam_infer.py) =================
MODEL_CONFIGS = [
    {
        "path": "models/isl_model_fold1.pt",
        "weight": 0.2,
        "dataset": "indian",             # Expects data/splits/indian_label_map.json
        "arch_fallback": "mobilenet_v2",
        "img_size_fallback": 96
    },
    {
        "path": "models/indian_mnv2_best.pt",
        "weight": 0.8,
        "dataset": "indian",
        "arch_fallback": "mobilenet_v2",
        "img_size_fallback": 96
    }
]

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class EnsembleISLModel:
    def __init__(self):
        self.models_list = []
        self.idx_to_label = None
        self.device = DEVICE

        # Standard ImageNet normalization
        self.base_norm = transforms.Normalize(
            [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
        )

        print(f"[INFO] Loading Ensemble on {self.device}...")

        for cfg in MODEL_CONFIGS:
            self._load_single_model(cfg)

        if not self.models_list:
            raise RuntimeError("No models were loaded!")

        # Use the first model's label map for display/return
        self.idx_to_label = self.models_list[0]["idx_to_label"]
        print(f"[SUCCESS] Ensemble loaded with {len(self.models_list)} models.")

    def _load_single_model(self, cfg):
        path = cfg["path"]
        if not Path(path).exists():
            print(f"[WARNING] Model not found: {path}. Skipping.")
            return

        try:
            ckpt = torch.load(path, map_location=self.device)

            # 1. Extract State Dict
            sd = ckpt["model_state"] if (isinstance(ckpt, dict) and "model_state" in ckpt) else ckpt

            # 2. Handle Label Map
            if isinstance(ckpt, dict) and "label_map" in ckpt:
                label_map = {k: int(v) for k, v in ckpt["label_map"].items()}
            else:
                label_map = self._load_fallback_label_map(cfg["dataset"])

            num_classes = len(label_map)
            idx_to_label = {v: k for k, v in label_map.items()}

            # 3. Handle Arch & Img Size
            arch = ckpt.get("arch", cfg.get("arch_fallback", "mobilenet_v2"))
            img_size = int(ckpt.get("img_size", cfg.get("img_size_fallback", 96)))

            # 4. Build Model
            model = self._build_arch(arch, num_classes)
            model.load_state_dict(sd, strict=False)
            model.to(self.device).eval()

            self.models_list.append({
                "model": model,
                "weight": cfg["weight"],
                "img_size": img_size,
                "idx_to_label": idx_to_label
            })
            print(f"  - Loaded {path} (w={cfg['weight']}, size={img_size})")

        except Exception as e:
            print(f"[ERROR] Failed to load {path}: {e}")

    def _load_fallback_label_map(self, dataset_name):
        # Assumes running from root, looking in data/splits/
        p = Path("data/splits") / f"{dataset_name}_label_map.json"
        if not p.exists():
            # Fallback for safety if file missing: return dummy map
            print(f"[WARN] Label map {p} not found. Creating dummy map.")
            return {str(i): i for i in range(100)}

        with open(p, "r", encoding="utf-8") as f:
            lm = json.load(f)
        return {k: int(v) for k, v in lm.items()}

    def _build_arch(self, arch, num_classes):
        if arch == "mobilenet_v2":
            m = models.mobilenet_v2(weights=None)
            m.classifier[1] = nn.Linear(m.classifier[1].in_features, num_classes)
            return m
        # Add other architectures here if needed (squeezenet etc)
        raise ValueError(f"Unsupported architecture: {arch}")

    def preprocess(self, pil_img, img_size):
        """
        Matches 3_webcam_infer.py logic:
        Resize -> Grayscale(1) -> ToTensor -> Repeat(3) -> Normalize
        """
        tfm = transforms.Compose([
            transforms.Resize((img_size, img_size), interpolation=InterpolationMode.BILINEAR),
            transforms.Grayscale(1),
            transforms.ToTensor(),
            lambda t: t.repeat(3, 1, 1), # Repeat 1 channel to 3
            self.base_norm
        ])
        return tfm(pil_img).unsqueeze(0).to(self.device)

    def predict(self, frame_bgr: np.ndarray):
        """
        Args:
            frame_bgr: OpenCV image (BGR) from the API request
        Returns:
            (gesture_label, confidence_score)
        """
        if frame_bgr is None or not self.models_list:
            return "Error", 0.0

        # Convert BGR (OpenCV) -> RGB (PIL)
        # This ensures consistency with the training script
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)

        final_probs = None

        with torch.no_grad():
            for entry in self.models_list:
                # Preprocess specifically for this model's expected size
                x = self.preprocess(pil_img, entry["img_size"])

                logits = entry["model"](x)
                probs = torch.softmax(logits, dim=1)[0]

                # Weighted sum
                weighted = entry["weight"] * probs
                if final_probs is None:
                    final_probs = weighted
                else:
                    final_probs += weighted

        # Extract result
        final_probs = final_probs.detach().cpu().numpy()
        idx = int(np.argmax(final_probs))
        confidence = float(final_probs[idx])

        # Normalize confidence if weights don't sum to 1.0 (optional, but good practice)
        total_weight = sum(m["weight"] for m in self.models_list)
        if total_weight > 0:
            confidence /= total_weight

        label = self.idx_to_label.get(idx, str(idx))

        return label, confidence

# Singleton Pattern
_model_instance = None

def get_model():
    global _model_instance
    if _model_instance is None:
        _model_instance = EnsembleISLModel()
    return _model_instance

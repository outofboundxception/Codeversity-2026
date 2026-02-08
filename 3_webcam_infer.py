# scripts/3_webcam_infer.py
# Robust webcam inference that supports BOTH checkpoint formats:
# (A) full checkpoint: {"model_state","label_map","img_size","arch",...}
# (B) plain state_dict only (no label_map/img_size/arch)
#
# Also supports per-model label_map fallback from JSON.

import cv2
import torch
import numpy as np
from pathlib import Path
from collections import deque
from torchvision import transforms, models
from torchvision.transforms import InterpolationMode
from PIL import Image
import torch.nn as nn
import json

# ================= CONFIG =================
MODEL_CONFIGS = [
    {
        "path": "models/isl_model_fold1.pt",
        "weight": 0.2,
        "dataset": "indian",            # label map fallback file: data/splits/indian_label_map.json
        "arch_fallback": "mobilenet_v2",# used only if checkpoint is state_dict-only
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

OUT_DIR = Path("outputs")
FRAME_DIR = OUT_DIR / "frames"
OUT_DIR.mkdir(exist_ok=True)
FRAME_DIR.mkdir(parents=True, exist_ok=True)

WINDOW = 16
CONF_THRESH = 0.6
CAM_ID = 0

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ================= HELPERS =================
def load_label_map(dataset_name: str):
    p = Path("data/splits") / f"{dataset_name}_label_map.json"
    if not p.exists():
        raise FileNotFoundError(f"Label map not found: {p}")
    lm = json.load(open(p, "r", encoding="utf-8"))
    # ensure values are ints
    return {k: int(v) for k, v in lm.items()}


def build_model(arch: str, num_classes: int):
    arch = (arch or "").lower()

    if arch == "squeezenet1_1":
        m = models.squeezenet1_1(weights=None)
        m.classifier[1] = nn.Conv2d(512, num_classes, kernel_size=1)
        return m

    if arch == "mobilenet_v2":
        m = models.mobilenet_v2(weights=None)
        m.classifier[1] = nn.Linear(m.classifier[1].in_features, num_classes)
        return m

    if arch == "mobilenet_v3_small":
        m = models.mobilenet_v3_small(weights=None)
        m.classifier[-1] = nn.Linear(m.classifier[-1].in_features, num_classes)
        return m

    raise ValueError(f"Unsupported architecture: {arch}")


def extract_state_dict(ckpt):
    # Full checkpoint style
    if isinstance(ckpt, dict) and "model_state" in ckpt:
        return ckpt["model_state"]
    # Plain state_dict style
    return ckpt


def infer_arch_from_state_dict_keys(sd):
    # Best-effort guess if you saved ONLY weights
    keys = list(sd.keys())
    if any(k.startswith("classifier.1.weight") for k in keys) and any("features." in k for k in keys):
        return "mobilenet_v2"
    if any(k.startswith("classifier.1.weight") for k in keys) and any("features." in k for k in keys):
        return "mobilenet_v2"
    # Squeezenet classifier conv weight often: "classifier.1.weight"
    # Not reliable; you should set arch_fallback in config.
    return None


# ================= LOAD MODELS (ROBUST) =================
models_list = []

# We'll use the first model's label map for displaying labels,
# but each model can load its own label_map (must match class order).
global_label_map = None
global_img_size = None

for cfg in MODEL_CONFIGS:
    path = cfg["path"]
    if not Path(path).exists():
        raise FileNotFoundError(f"Model file not found: {path} (run from project root so 'models/' is visible)")

    ckpt = torch.load(path, map_location=DEVICE)
    sd = extract_state_dict(ckpt)

    # Label map handling
    if isinstance(ckpt, dict) and "label_map" in ckpt:
        label_map = ckpt["label_map"]
        # ensure ints
        label_map = {k: int(v) for k, v in label_map.items()}
    else:
        # fallback to json
        label_map = load_label_map(cfg["dataset"])

    idx_to_label = {v: k for k, v in label_map.items()}
    num_classes = len(label_map)

    # img size handling
    if isinstance(ckpt, dict) and "img_size" in ckpt:
        img_size = int(ckpt["img_size"])
    else:
        img_size = int(cfg.get("img_size_fallback", 96))

    # arch handling
    if isinstance(ckpt, dict) and "arch" in ckpt:
        arch = ckpt["arch"]
    else:
        arch = infer_arch_from_state_dict_keys(sd) or cfg.get("arch_fallback", "mobilenet_v2")

    # Build + load
    model = build_model(arch, num_classes)
    missing, unexpected = model.load_state_dict(sd, strict=False)
    # strict=False helps when checkpoints have small metadata differences

    model.to(DEVICE).eval()

    models_list.append({
        "model": model,
        "weight": float(cfg["weight"]),
        "idx_to_label": idx_to_label,
        "img_size": img_size,
        "arch": arch,
        "path": path
    })

    # Choose global (display) mapping from first model
    if global_label_map is None:
        global_label_map = label_map
        global_img_size = img_size

print(f"[INFO] Loaded {len(models_list)} models on {DEVICE}")
for m in models_list:
    print(f"  - {m['path']} | arch={m['arch']} | classes={len(m['idx_to_label'])} | img={m['img_size']} | w={m['weight']}")


# ================= TRANSFORM =================
# IMPORTANT: Your earlier training used grayscale->repeat to 3 channels.
# We keep it, but use each model's img_size by resizing dynamically in loop.
base_norm = transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])

def preprocess(pil_img: Image.Image, img_size: int):
    tfm = transforms.Compose([
        transforms.Resize((img_size, img_size), interpolation=InterpolationMode.BILINEAR),
        transforms.Grayscale(1),
        transforms.ToTensor(),
        lambda t: t.repeat(3, 1, 1),
        base_norm
    ])
    return tfm(pil_img)


# ================= TEMPORAL BUFFERS =================
pred_buf = deque(maxlen=WINDOW)
conf_buf = deque(maxlen=WINDOW)

# ================= VIDEO IO =================
cap = cv2.VideoCapture(CAM_ID)

# Use actual webcam resolution if available
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
if w <= 0 or h <= 0:
    w, h = 640, 480

fourcc = cv2.VideoWriter_fourcc(*"XVID")
out_vid = cv2.VideoWriter(str(OUT_DIR / "webcam_ensemble.avi"), fourcc, 20.0, (w, h))

frame_count = 0
print("[INFO] Webcam started — press Q to quit")

# ================= MAIN LOOP =================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # Save frame
    cv2.imwrite(str(FRAME_DIR / f"frame_{frame_count:06d}.jpg"), frame)

    # Convert to PIL
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # -------- Ensemble Prediction --------
    final_probs = None
    chosen_idx_to_label = models_list[0]["idx_to_label"]  # display mapping

    with torch.no_grad():
        for entry in models_list:
            x = preprocess(img, entry["img_size"]).unsqueeze(0).to(DEVICE)

            logits = entry["model"](x)
            probs = torch.softmax(logits, dim=1)[0]

            weighted = entry["weight"] * probs
            final_probs = weighted if final_probs is None else (final_probs + weighted)

    final_probs = final_probs.detach().cpu().numpy()

    idx = int(np.argmax(final_probs))
    conf = float(final_probs[idx])

    pred_buf.append(idx)
    conf_buf.append(conf)

    # -------- Temporal Smoothing --------
    if len(pred_buf) == WINDOW:
        vals, counts = np.unique(pred_buf, return_counts=True)
        smooth_idx = int(vals[np.argmax(counts)])
        smooth_conf = float(np.mean(conf_buf))
    else:
        smooth_idx = idx
        smooth_conf = conf

    label = chosen_idx_to_label.get(smooth_idx, str(smooth_idx))

    # -------- Display --------
    text = f"{label} ({smooth_conf:.2f})"
    color = (0, 255, 0) if smooth_conf > CONF_THRESH else (0, 0, 255)

    cv2.putText(frame, text, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("ISL Ensemble Webcam", frame)
    out_vid.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ================= CLEANUP =================
cap.release()
out_vid.release()
cv2.destroyAllWindows()

print("[DONE] Video and frames saved in /outputs")

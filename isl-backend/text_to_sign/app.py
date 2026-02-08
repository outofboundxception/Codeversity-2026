from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from isl_model import generate_isl_sequence

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
SIGN_ASSETS_DIR = BASE_DIR / "sign_assets"

print("BASE_DIR =", BASE_DIR)
print("SIGN_ASSETS_DIR =", SIGN_ASSETS_DIR)

app.mount(
    "/signs",
    StaticFiles(directory=str(SIGN_ASSETS_DIR)),
    name="signs"
)

class TextRequest(BaseModel):
    text: str

@app.post("/predict")
def predict(req: TextRequest):
    print("Received text:", req.text)

    images = generate_isl_sequence(req.text)

    urls = []
    for img in images:
        p = Path(img)
        urls.append(f"/signs/{p.parent.name}/{p.name}")

    return {
        "text": req.text,
        "images": urls
    }

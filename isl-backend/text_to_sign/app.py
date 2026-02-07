from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from isl_model import generate_isl_sequence

app = FastAPI()

app.mount("/signs", StaticFiles(directory="sign_assets"), name="signs")

class TextRequest(BaseModel):
    text: str

@app.post("/predict")
def predict(req: TextRequest):
    images = generate_isl_sequence(req.text)

    urls = [img.replace("sign_assets", "/signs") for img in images]

    return {
        "text": req.text,
        "images": urls
    }

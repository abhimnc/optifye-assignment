from fastapi import FastAPI, UploadFile, File
from app.model import model
from app.utils import preprocess
import torch
import requests
import base64

app = FastAPI()

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image_tensor = preprocess(image_bytes)
    with torch.no_grad():
        prediction = model([image_tensor])[0]

    data = {
        "boxes": prediction["boxes"].tolist(),
        "labels": prediction["labels"].tolist(),
        "scores": prediction["scores"].tolist(),
        "image": base64.b64encode(image_bytes).decode("utf-8")
    }

    # Send to Flask
    response = requests.post("http://13.50.65.62:5555/draw", json=data)
    return {"processed_image": response.json()["image"]}
from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List
import os
from PIL import Image
import io

app = FastAPI()
SHARED_DATA_PATH = "/usr/src/shared-volume/"

@app.get("/")
async def root():
    return {"message": "Backend is running"}


@app.post("/model/add_class")
async def add_class(label: str, data: List[UploadFile] = File(...)):
    try:
        os.mkdir(f"{SHARED_DATA_PATH}/images/{label}")
    except:
        pass
    print(data)
    for img in data:
        img_file = Image.open(img)
        img_file.save(f"{SHARED_DATA_PATH}/images/{label}/{img.filename}")
    # send to model service
    return {"message": "Class added successfully"}

@app.get("/model/classes")
async def get_classes():
    try:
        classes = os.listdir(f"{SHARED_DATA_PATH}/images")
    except:
        raise HTTPException(status_code=400, detail="No classes found")
    return {"classes": classes }

@app.get("/model/train")
async def train():
    # send to model service
    return {"message": "Model trained successfully"}


@app.post("/model/predict")
async def predict(data: List):
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Data cannot be empty")
    # send to model service
    return {"message": "Prediction successful"}


@app.post("/model/upload")
async def upload(file):
    if file.filename == "":
        raise HTTPException(status_code=400, detail="File cannot be empty")
    # send to model service
    return {"message": "File uploaded successfully"}

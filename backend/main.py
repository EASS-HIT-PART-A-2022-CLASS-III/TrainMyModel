from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List, Annotated, TextIO

import shutil
import os
from PIL import Image
import io

app = FastAPI()
SHARED_DATA_PATH = "/usr/src/shared-volume/"

app.add_event_handler("startup", lambda: os.makedirs(f"{SHARED_DATA_PATH}/images", exist_ok=True))
app.add_event_handler("startup", lambda: os.makedirs(f"{SHARED_DATA_PATH}/model", exist_ok=True))



@app.get("/")
async def root():
    return {"message": "Backend is running"}


@app.post("/model/classes/add")
async def add_class(label: str, number_of_images: int):

    return {"message": f"Class {label} added {number_of_images} images successfully"}
    # return {"message": "Yes"}

@app.post("/model/classes/delete")
async def add_class(label: str):
    
    classes = os.listdir(f"{SHARED_DATA_PATH}/images")
    if label not in classes:
        raise HTTPException(status_code=400, detail="Class not found")
    else:
        shutil.rmtree(f"{SHARED_DATA_PATH}/images/{label}", ignore_errors=True )

    return {"message": f"Class {label} deleted successfully"}


@app.get("/model/classes")
async def get_classes():
    try:
        gold_labels = os.listdir(f"{SHARED_DATA_PATH}/images")
        for label in gold_labels:
            print(label)
            print(len(os.listdir(f"{SHARED_DATA_PATH}/images/{label}")))
        classes = {class_ : len(os.listdir(f"{SHARED_DATA_PATH}/images/{class_}")) for class_ in os.listdir(f"{SHARED_DATA_PATH}/images")}
        # os.listdir(f"{SHARED_DATA_PATH}/images")
        
        # print(classes)
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

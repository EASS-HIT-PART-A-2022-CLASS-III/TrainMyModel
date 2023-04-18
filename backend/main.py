from fastapi import FastAPI, HTTPException
from typing import List


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Backend is running"}


@app.post("/model/add_class")
async def add_class(label: str, data: List):
    if label == "":
        raise HTTPException(status_code=400, detail="Label cannot be empty")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Data cannot be empty")
    # send to model service

    return {"message": "Class added successfully"}


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

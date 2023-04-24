from fastapi import FastAPI, HTTPException, status
from typing import List
import shutil
import os
import httpx
import datetime
import asyncio

app = FastAPI()
SHARED_DATA_PATH = "/usr/src/shared-volume/"


@app.on_event("startup")
def init_data():
    os.makedirs(f"{SHARED_DATA_PATH}/images", exist_ok=True)
    os.makedirs(f"{SHARED_DATA_PATH}/model", exist_ok=True)
    
    app.model_status = {
        "data": {},
        "model_info": {
            "status": "not trained",
            "train_params": None,
            "start_time": None,
            "end_time": None,
            "evaluation": None,
        },
    }
    cls = os.listdir(f"{SHARED_DATA_PATH}/images")
    if len(cls) > 0:
            for folder in cls:
                
                app.model_status["data"][folder] = len(os.listdir(f"{SHARED_DATA_PATH}/images/{folder}"))


@app.get("/")
async def root():
    return {"message": "Backend is running"}

@app.post("/model/classes/add")
async def add_class(label: str, number_of_images: int):
    # create class folder in shared volume
    os.makedirs(f"{SHARED_DATA_PATH}/images/{label}", exist_ok=True)

    
    if label not in app.model_status["data"]:
        app.model_status["data"][label] = number_of_images
    else:
        app.model_status["data"][label] += number_of_images

    return {"message": f"Class {label} added {number_of_images} images successfully"}


@app.post("/model/classes/delete")
async def delete_class(label: str):
    if label not in app.model_status["data"]:
        raise HTTPException(status_code=400, detail="Class not found")
    else:
        
        del app.model_status["data"][label]
        shutil.rmtree(f"{SHARED_DATA_PATH}/images/{label}", ignore_errors=True)

    return {"message": f"Class {label} deleted successfully"}


@app.post("/model/classes/update")
async def update_class(oldlabel: str, newlabel: str):
    if oldlabel not in app.model_status["data"]:
        raise HTTPException(status_code=400, detail="Class not found")
    else:
        
        app.model_status["data"][newlabel] = app.model_status["data"][oldlabel]
        del app.model_status["data"][oldlabel]

        os.rename(
            os.path.join(f"{SHARED_DATA_PATH}/images/", oldlabel),
            os.path.join(f"{SHARED_DATA_PATH}/images/", newlabel),
        )
    return {"message": f"Class {oldlabel} changed to {newlabel} successfully"}


@app.get("/model/classes")
async def get_classes():
    return app.model_status["data"]


@app.post("/model/train")
async def train(batch_size: int, epochs: int):
    if batch_size <= 0:
        raise HTTPException(status_code=400, detail="Batch size cannot be less than or equal to 0")
    if epochs <= 0:
        raise HTTPException(status_code=400, detail="Epochs cannot be less than or equal to 0")
    if len(os.listdir(f"{SHARED_DATA_PATH}/images")) == 0:
        raise HTTPException(status_code=400, detail="No classes found")

    
    app.model_status["model_info"]["status"] = "training"
    app.model_status["model_info"]["train_params"] = {"batch_size": batch_size, "epochs": epochs}
    app.model_status["model_info"]["start_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with httpx.AsyncClient() as client:
        eval = await client.get(
            "http://mymodel:8002/model/train", params=app.model_status["model_info"]["train_params"], timeout=None
        )
    # send to model service
    app.model_status["model_info"]["status"] = "trained"
    app.model_status["model_info"]["end_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.model_status["model_info"]["evaluation"] = eval.json()
    print("done")
    print(app.model_status)
    return {"message": "Model training finished"}



@app.get("/model/status")
async def get_status():
    return app.model_status


@app.post("/model/predict")
async def predict(data: List):
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Data cannot be empty")
    # send to model service
    async with httpx.AsyncClient() as client:
        eval = await client.post(
            "http://mymodel:8002/model/predict", params={'data':data}, timeout=None
        )
    return eval


@app.post("/model/upload")
async def upload(file):
    if file.filename == "":
        raise HTTPException(status_code=400, detail="File cannot be empty")
    # send to model service
    return {"message": "File uploaded successfully"}

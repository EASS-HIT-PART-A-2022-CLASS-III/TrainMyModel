from fastapi import FastAPI, HTTPException, UploadFile, File
# from fastapi.responses import FileResponse
from typing import List
import shutil
import os
import httpx
import datetime

############ APP INIT ############

app = FastAPI()

SHARED_DATA_PATH = os.getenv("SHARED_VOLUME")
MYMODEL_URL = os.getenv("MYMODEL_URL")

@app.on_event("startup")
def init_data():
    # create shared volume folders
    os.makedirs(f"{SHARED_DATA_PATH}/images", exist_ok=True)
    os.makedirs(f"{SHARED_DATA_PATH}/model", exist_ok=True)
    os.makedirs(f"{SHARED_DATA_PATH}/output", exist_ok=True)
    
    # init model status
    app.model_status = {
        "data": {},
        "model_info": {
            "status": "not trained",
            "train_params": None,
            "train_size": None,
            "val_size": None,
            "start_time": None,
            "end_time": None,
            "evaluation": None,
        },
    }

    # get classes from shared folder
    cls = os.listdir(f"{SHARED_DATA_PATH}/images")
    if len(cls) > 0:
        for folder in cls:
            app.model_status["data"][folder] = len(os.listdir(f"{SHARED_DATA_PATH}/images/{folder}"))

############ ROUTES ############

@app.get("/")
async def root():
    return {"message": "Backend is running"}


########## CLASSES MANAGEMENT ROUTES ##########

@app.get("/model/classes")
async def get_classes():
    return app.model_status["data"]


@app.post("/model/classes/add")
async def add_class(label: str, number_of_images: int):
    # create class folder in shared volume
    os.makedirs(f"{SHARED_DATA_PATH}/images/{label}", exist_ok=True)

    # add class to model status
    if label not in app.model_status["data"]:
        app.model_status["data"][label] = number_of_images
    else:
        app.model_status["data"][label] += number_of_images

    return {"message": f"Class {label} added {number_of_images} images successfully"}


@app.post("/model/classes/update")
async def update_class(oldlabel: str, newlabel: str):
    # check if class exists
    if oldlabel not in app.model_status["data"]:
        raise HTTPException(status_code=400, detail="Class not found")
    else:
        # update class name in model status
        app.model_status["data"][newlabel] = app.model_status["data"][oldlabel]
        del app.model_status["data"][oldlabel]

        # update class name in shared volume
        os.rename(
            os.path.join(f"{SHARED_DATA_PATH}/images/", oldlabel),
            os.path.join(f"{SHARED_DATA_PATH}/images/", newlabel),
        )
    return {"message": f"Class {oldlabel} changed to {newlabel} successfully"}

@app.post("/model/classes/delete")
async def delete_class(label: str):
    # check if class exists
    if label not in app.model_status["data"]:
        raise HTTPException(status_code=400, detail="Class not found")
    else:
        # delete class from model status
        del app.model_status["data"][label]

        # delete class from shared volume
        shutil.rmtree(f"{SHARED_DATA_PATH}/images/{label}", ignore_errors=True)

    return {"message": f"Class {label} deleted successfully"}


########## MODEL MANAGEMENT ROUTES ##########

@app.get("/model/status")
async def get_status():
    return app.model_status

@app.post("/model/train")
async def train(batch_size: int, epochs: int):
    # check training parameters
    if batch_size <= 0:
        raise HTTPException(status_code=400, detail="Batch size cannot be less than or equal to 0")
    if epochs <= 0:
        raise HTTPException(status_code=400, detail="Epochs cannot be less than or equal to 0")
    if len(os.listdir(f"{SHARED_DATA_PATH}/images")) == 0:
        raise HTTPException(status_code=400, detail="No classes found")

    # update model status
    app.model_status["model_info"]["status"] = "training"
    app.model_status["model_info"]["train_params"] = {"batch_size": batch_size, "epochs": epochs}
    app.model_status["model_info"]["start_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # strat training in model service
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{MYMODEL_URL}/model/train", params=app.model_status["model_info"]["train_params"], timeout=None
        )
    res = res.json()
    
    # update model status
    app.model_status["model_info"]["status"] = "trained"
    app.model_status["model_info"]["end_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.model_status["model_info"]["train_size"] = res['train_size']
    app.model_status["model_info"]["val_size"] = res['val_size']
    app.model_status["model_info"]["evaluation"] = res['eval']
    
    return {"message": "Model training finished"}


@app.get("/model/delete")
async def delete_model():
    # send to model service
    async with httpx.AsyncClient() as client:
        await client.get(f"{MYMODEL_URL}/model/delete", timeout=None)
    
    # update model status
    app.model_status["model_info"]["status"] = "not trained"
    app.model_status["model_info"]["train_params"] = None
    app.model_status["model_info"]["train_size"] = None
    app.model_status["model_info"]["val_size"] = None
    app.model_status["model_info"]["start_time"] = None
    app.model_status["model_info"]["end_time"] = None
    app.model_status["model_info"]["evaluation"] = None

    return {"message": "Model deleted successfully"}

@app.post("/model/predict")
async def predict(file : UploadFile = File(...)):
    # save file to shared folder
    filename = file.filename
    path = f"{SHARED_DATA_PATH}/output/{filename}"
    with open(path, 'wb') as f:
        content = await file.read()
        f.write(content)

    # send to model service
    async with httpx.AsyncClient() as client:
        eval = await client.post(
            f"{MYMODEL_URL}/model/predict", params={'filename':filename}, timeout=None
        )
        
    return eval


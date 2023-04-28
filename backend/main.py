from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
import httpx
import shutil
import os
import datetime
import json


############ DATA CLASS ############


# class DataClass(BaseModel):
#     name: str
#     samples: int


############ APP INIT ############

app = FastAPI(title="TrainMyModel Backend", version="0.1.0")

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
        "data": [],
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
            samples = len(os.listdir(f"{SHARED_DATA_PATH}/images/{folder}"))
            app.model_status["data"].append({'name':folder, 'samples':samples})

    # load model from shared folder
    if os.path.isfile(f"{SHARED_DATA_PATH}/model/model_status.json"):
        with open(f"{SHARED_DATA_PATH}/model/model_status.json", "r") as f:
            app.model_status = json.loads(f.read())
        
    
# @app.on_event("shutdown")
# def shutdown():
    # delete output folder
    # shutil.rmtree(f"{SHARED_DATA_PATH}/output")



############ ROUTES ############

@app.get("/")
async def root():
    return {"message": "Backend is running"}


########## CLASS MANAGEMENT ROUTES ##########
# CRUD operations for classes management
# All classes are stored in shared volume
# app.model_status['data'] is used to keep track of classes and is updated when a class is added, updated or deleted


@app.get("/classes")
async def get_classes():
    # cls_names = {cls.name: cls.samples for cls in app.model_status["data"]}
    return app.model_status["data"]


@app.post("/classes/add")
async def add_class(label: str, number_of_images: int):
    # create class folder in shared volume
    os.makedirs(f"{SHARED_DATA_PATH}/images/{label}", exist_ok=True)

    # add class to model status
    for data_class in app.model_status["data"]:
        if data_class['name'] == label:
            data_class['samples'] += number_of_images
            break
    else:
        app.model_status["data"].append({'name':label, 'samples':number_of_images})

    return {"message": f"Class {label} added {number_of_images} images successfully"}


@app.post("/classes/update")
async def update_class(oldlabel: str, newlabel: str):
    # check if class exists
    current_class = None
    for data_class in app.model_status["data"]:
        if data_class['name'] == newlabel:
            raise HTTPException(
                status_code=400, detail="Can't rename to an existing class"
            )
        if data_class['name'] == oldlabel:
            current_class = data_class
            
            break

    if not current_class:
        raise HTTPException(status_code=400, detail="Class not found")

    # update class name in model status
    current_class['name'] = newlabel
    

    # update class name in shared volume
    os.rename(
        os.path.join(f"{SHARED_DATA_PATH}/images/", oldlabel),
        os.path.join(f"{SHARED_DATA_PATH}/images/", newlabel),
    )
    return {"message": f"Class {oldlabel} changed to {newlabel} successfully"}


@app.post("/classes/delete")
async def delete_class(label: str):
    # check if class exists
    current_class = None
    for data_class in app.model_status["data"]:
        if data_class['name'] == label:
            current_class = data_class
            break

    if not current_class:
        raise HTTPException(status_code=400, detail="Class not found")

    # delete class from model status
    app.model_status["data"].remove(current_class)
    print(app.model_status["data"])
    
    # delete class from shared volume
    shutil.rmtree(f"{SHARED_DATA_PATH}/images/{label}", ignore_errors=True)

    return {"message": f"Class {label} deleted successfully"}


########## MODEL MANAGEMENT ROUTES ##########
# operations for model management
# The model is trained in mymodel service
# app.model_status['model_info'] is used to keep track of the model and its status


@app.get("/model/status")
async def get_status():
    return app.model_status


@app.post("/model/train")
async def train(batch_size: int, epochs: int, optimizer:str, learning_rate: float, momentum:float, loss: str):
    # check training parameters
    if batch_size <= 0:
        raise HTTPException(
            status_code=400, detail="Batch size cannot be less than or equal to 0"
        )
    if epochs <= 0:
        raise HTTPException(
            status_code=400, detail="Epochs cannot be less than or equal to 0"
        )
    
    if len(os.listdir(f"{SHARED_DATA_PATH}/images")) == 0:
        raise HTTPException(status_code=400, detail="No classes found")

    # update model status
    app.model_status["model_info"]["status"] = "training"
    app.model_status["model_info"]["train_params"] = {
        "batch_size": batch_size,
        "epochs": epochs,
        "optimizer": optimizer,
        "learning_rate": learning_rate,
        "momentum": momentum,
        "loss": loss,
    }
    app.model_status["model_info"]["start_time"] = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # start training in mymodel service and wait for response
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{MYMODEL_URL}/model/train",
            params=app.model_status["model_info"]["train_params"],
            timeout=None,
        )
    res = res.json()

    # update model status after training
    app.model_status["model_info"]["status"] = "trained"
    app.model_status["model_info"]["end_time"] = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    app.model_status["model_info"]["train_size"] = res["train_size"]
    app.model_status["model_info"]["val_size"] = res["val_size"]
    app.model_status["model_info"]["evaluation"] = res["eval"]

    # save model status to shared volume
    
    with open(f"{SHARED_DATA_PATH}/model/model_status.json", "w") as f:
        json.dump(app.model_status, f)

    return {"message": "Model training finished"}


@app.get("/model/delete")
async def delete_model():
    # send to mymodel service
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
async def predict(file: UploadFile = File(...)):
    # save file to shared folder
    filename = file.filename
    path = f"{SHARED_DATA_PATH}/output/{filename}"
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    classes = [cls.name for cls in app.model_status["data"]]

    # send to model service
    async with httpx.AsyncClient() as client:
        eval = await client.post(
            f"{MYMODEL_URL}/model/predict",
            json={"path_to_img": path, "classes": classes},
            timeout=None,
        )

    return eval.json()

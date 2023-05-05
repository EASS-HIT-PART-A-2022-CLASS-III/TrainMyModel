from schemas import ImageData
import datetime
import shutil
import os
import io
import base64
import json
import random
import httpx
from PIL import Image
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.testclient import TestClient


############ DOCKER-COMPOSE ENV ############

SHARED_DATA_PATH = os.getenv("SHARED_VOLUME")
MYMODEL_URL = os.getenv("MYMODEL_URL")

############ APP INIT ############

app = FastAPI(title="TrainMyModel Backend", version="0.1.0")

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
            "summary": None,
        },
    }

    # load model from shared folder
    if os.path.isfile(f"{SHARED_DATA_PATH}/model/model_status.json"):
        with open(f"{SHARED_DATA_PATH}/model/model_status.json", "r") as f:
            app.model_status.update(json.loads(f.read()))

    # get classes from shared folder
    cls = os.listdir(f"{SHARED_DATA_PATH}/images")
    
    if len(cls) > 0:
        # empty app.model_status["data"]
        for folder in cls:
            if folder not in [data_class["name"] for data_class in app.model_status["data"]]:
                samples = len(os.listdir(f"{SHARED_DATA_PATH}/images/{folder}"))
                app.model_status["data"].append({"name": folder, "samples": samples})
                app.model_status["model_info"]["status"] = "data changed"


@app.on_event("shutdown")
def shutdown():
    # delete output folder content on shutdown
    # besides model_weights.zip, which is used by mymodel service
    for filename in os.listdir(f"{SHARED_DATA_PATH}/output"):
        if filename != "model_weights.zip":
            os.remove(f"{SHARED_DATA_PATH}/output/{filename}")


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
    data = app.model_status["data"]
    return data
    

@app.get("/classes/get_images/{label}", response_model=ImageData)
async def get_images(label: str, num: int = 3):
    # check if class exists
    current_class = None
    for data_class in app.model_status["data"]:
        if data_class["name"] == label:
            current_class = data_class
            break

    if not current_class:
        raise HTTPException(status_code=400, detail="Class not found")

    image_data = {'images':[], 'label':label}
    # get images from shared volume
    images = os.listdir(f"{SHARED_DATA_PATH}/images/{label}")
    for _ in range(num):
        rnd_image = random.choice(images)
        images.remove(rnd_image)
        image = Image.open(f"{SHARED_DATA_PATH}/images/{label}/{rnd_image}")
        image = image.resize((224, 224))
        image_bytes = io.BytesIO()
        format = 'png'
        
        image.save(image_bytes, format=format)
        content = base64.b64encode(image_bytes.getvalue())
        img_scheme = {'img':content.decode(), 'filename':rnd_image}
        image_data['images'].append(img_scheme)

    return image_data
     


@app.post("/classes/add")
async def add_class(data :ImageData):
    label = data.label
    images = data.images

    print(len(images), label)
    # create class folder in shared volume
    if not os.path.exists(f"{SHARED_DATA_PATH}/images/{label}"):

        os.makedirs(f"{SHARED_DATA_PATH}/images/{label}", exist_ok=True)
    
    # save images to shared volume
    for img_str in images:
        image = Image.open(io.BytesIO(base64.b64decode(img_str.img.encode())))
        image.save(f"{SHARED_DATA_PATH}/images/{label}/{img_str.filename}")
    
    number_of_images = len(images)

    # add class to model status
    for data_class in app.model_status["data"]:
        if data_class["name"] == label:
            data_class["samples"] += number_of_images
            break
    else:
        app.model_status["data"].append({"name": label, "samples": number_of_images})
    
    app.model_status["model_info"]["status"] = "data changed"

    return {"message": f"Class {label} added {number_of_images} images successfully"}


@app.post("/classes/update")
async def update_class(oldlabel: str, newlabel: str):
    # check if class exists
    current_class = None
    for data_class in app.model_status["data"]:
        if data_class["name"] == newlabel:
            raise HTTPException(
                status_code=400, detail="Can't rename to an existing class"
            )
        if data_class["name"] == oldlabel:
            current_class = data_class

            break

    if not current_class:
        raise HTTPException(status_code=400, detail="Class not found")

    # update class name in model status
    current_class["name"] = newlabel

    # update class name in shared volume
    os.rename(
        os.path.join(f"{SHARED_DATA_PATH}/images/", oldlabel),
        os.path.join(f"{SHARED_DATA_PATH}/images/", newlabel),
    )

    app.model_status["model_info"]["status"] = "data changed"

    return {"message": f"Class {oldlabel} changed to {newlabel} successfully"}


@app.post("/classes/delete")
async def delete_class(label: str):
    # check if class exists
    current_class = None
    for data_class in app.model_status["data"]:
        if data_class["name"] == label:
            current_class = data_class
            break

    if not current_class:
        raise HTTPException(status_code=400, detail="Class not found")

    # delete class from model status
    app.model_status["data"].remove(current_class)
 
    # delete class from shared volume
    shutil.rmtree(f"{SHARED_DATA_PATH}/images/{label}", ignore_errors=True)

    app.model_status["model_info"]["status"] = "data changed"

    return {"message": f"Class {label} deleted successfully"}


########## MODEL MANAGEMENT ROUTES ##########
# operations for model management
# The model is trained in mymodel service
# app.model_status['model_info'] is used to keep track of the model and its status


@app.get("/model/status")
async def get_status():
    return app.model_status

@app.get("/model/download")
async def download_model():
    # check if model exists
    if not os.path.exists(f"{SHARED_DATA_PATH}/output/model_weights.zip"):
        raise HTTPException(status_code=400, detail="Model weights not found")

    # download model
    return FileResponse(f"{SHARED_DATA_PATH}/output/model_weights.zip", media_type="application/zip", filename="model_weights.zip")

@app.get("/model/architecture")
async def get_architecture():
    # check if model exists
    if not os.path.exists(f"{SHARED_DATA_PATH}/model/vis-model.png"):
        raise HTTPException(status_code=400, detail="Model architecture not found")

    image = Image.open(f"{SHARED_DATA_PATH}/model/vis-model.png")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='png')
    content = base64.b64encode(image_bytes.getvalue())
    return content

@app.post("/model/train")
async def train(
    batch_size: int,
    epochs: int,
    optimizer: str,
    learning_rate: float,
    momentum: float,
    loss: str,
):
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
    app.model_status["model_info"]["summary"] = res["summary"]

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
    app.model_status["model_info"]["summary"] = None

    return {"message": "Model deleted successfully"}


@app.post("/model/predict")
async def predict(img: ImageData):
    # save file to shared folder
    filename = img.images[0].filename
    path = f"{SHARED_DATA_PATH}/output/{filename}"
    content = img.images[0].img
    content = base64.b64decode(content.encode())
    # content = io.BytesIO(content)

    with open(path, "wb") as f:
        f.write(content)

    classes = [cls['name'] for cls in app.model_status["data"]]

    # send to model service
    async with httpx.AsyncClient() as client:
        eval = await client.post(
            f"{MYMODEL_URL}/model/predict",
            json={"path_to_img": path, "classes": classes},
            timeout=None,
        )

    return eval.json()


############ PYTESTS TESTS ############
# Testing the CRUD operations for classes management
# Using 'with TestClient' to test the environment variables in the app

def test_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Backend is running"}


def test_get_classes():
    with TestClient(app) as client:
        response = client.get("/classes")
        assert response.status_code == 200
        assert response.json() == []


def test_add_class():
    with TestClient(app) as client:
        response = client.post(
            "/classes/add", params={"label": "test", "number_of_images": 5}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Class test added 5 images successfully"}


def test_update_class():
    with TestClient(app) as client:
        response = client.post(
            "/classes/update", params={"oldlabel": "test", "newlabel": "test2"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Class test changed to test2 successfully"
        }


def test_get_classes_after_update():
    with TestClient(app) as client:
        response = client.get("/classes")
        assert response.status_code == 200
        assert {"name": "test", "samples": 0} not in response.json()
        assert {"name": "test2", "samples": 0} in response.json()


def test_delete_class():
    with TestClient(app) as client:
        response = client.post("/classes/delete", params={"label": "test2"})
        assert response.status_code == 200
        assert response.json() == {"message": "Class test2 deleted successfully"}

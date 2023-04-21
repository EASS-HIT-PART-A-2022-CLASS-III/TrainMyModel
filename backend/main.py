from fastapi import FastAPI, HTTPException
from typing import List
import shutil
import os
import httpx


app = FastAPI()
SHARED_DATA_PATH = "/usr/src/shared-volume/"

app.add_event_handler(
    "startup", lambda: os.makedirs(f"{SHARED_DATA_PATH}/images", exist_ok=True)
)
app.add_event_handler(
    "startup", lambda: os.makedirs(f"{SHARED_DATA_PATH}/model", exist_ok=True)
)


@app.get("/")
async def root():
    return {"message": "Backend is running"}


@app.post("/model/classes/add")
async def add_class(label: str, number_of_images: int):
    return {"message": f"Class {label} added {number_of_images} images successfully"}


@app.post("/model/classes/delete")
async def delete_class(label: str):

    classes = os.listdir(f"{SHARED_DATA_PATH}/images")
    if label not in classes:
        raise HTTPException(status_code=400, detail="Class not found")
    else:
        shutil.rmtree(f"{SHARED_DATA_PATH}/images/{label}", ignore_errors=True)

    return {"message": f"Class {label} deleted successfully"}


@app.post("/model/classes/update")
async def update_class(oldlabel: str, newlabel: str):

    classes = os.listdir(f"{SHARED_DATA_PATH}/images")
    if oldlabel not in classes:
        raise HTTPException(status_code=400, detail="Class not found")
    else:
        os.rename(
            os.path.join(f"{SHARED_DATA_PATH}/images/", oldlabel),
            os.path.join(f"{SHARED_DATA_PATH}/images/", newlabel),
        )
    return {"message": f"Class {oldlabel} changed to {newlabel} successfully"}


@app.get("/model/classes")
async def get_classes():
    try:
        classes = {
            class_: len(os.listdir(f"{SHARED_DATA_PATH}/images/{class_}"))
            for class_ in os.listdir(f"{SHARED_DATA_PATH}/images")
        }
    except:
        raise HTTPException(status_code=400, detail="No classes found")
    return {"classes": classes}


@app.post("/model/train")
async def train(batch_size: int, epochs: int):
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

    # send to model service

    httpx.post(
        "http://mymodel:8002/model/train",
        params={"batch_size": batch_size, "epochs": epochs},
    )

    return {
        "message": "Model started training",
        "batch_size": batch_size,
        "epochs": epochs,
    }


@app.post("/model/train/done")
async def train_done(evaluation: str):
    r = {"message": "Model training done", "evaluation": evaluation}
    print(r)
    httpx.post("http://frontend:8000/model/train/done", json=r)


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

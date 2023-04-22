from model import MyModel
from typing import List
import tensorflow as tf
from keras import layers
import fastapi
import httpx
import services

import numpy as np

SHARED_DATA_PATH = "/usr/src/shared-volume"
IMG_DATA_PATH = f"{SHARED_DATA_PATH}/images"

app = fastapi.FastAPI()
model = None
train_ds = None

# root


@app.get("/")
async def root():
    return {"message": "model is running"}


# train the model
@app.get("/model/train", response_model=None)
async def train(batch_size: int, epochs: int):
    
    train_ds, val_ds = services.get_datasets(IMG_DATA_PATH, batch_size)
    
    global model
    model = MyModel(len(train_ds.class_names))

    history = services.train_model(model, train_ds, val_ds, epochs)
    # grade the model
    acc = history.history["accuracy"]
    val_acc = history.history["val_accuracy"]

    loss = history.history["loss"]
    val_loss = history.history["val_loss"]

    services.save_model(model, SHARED_DATA_PATH)
    
    eval =  {
        "message": "Model trained successfully",
        "accuracy": acc,
        "val_accuracy": val_acc,
        "loss": loss,
        "val_loss": val_loss,
    }
    await httpx.post("http://backend:8000/model/train/done", params={'eval':eval})



# predict the class of the data
@app.post("/model/predict")
async def predict(data):
    if model is None:
        raise fastapi.HTTPException(status_code=400, detail="Model not trained")

    # load the image
    img = tf.keras.utils.load_img(data, target_size=(224, 224))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    return {
        "message": "Prediction successful",
        "class": train_ds.class_names[np.argmax(score)],
        "score": 100 * np.max(score),
    }

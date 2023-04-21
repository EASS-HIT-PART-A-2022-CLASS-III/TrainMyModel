from model import MyModel
from typing import List
import tensorflow as tf
from keras import layers
import fastapi
import httpx

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
@app.post("/model/train")
async def train(batch_size: int, epochs: int):
    # load the data from the data folder
    train_ds = tf.keras.utils.image_dataset_from_directory(
        IMG_DATA_PATH,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(224, 224),
        batch_size=batch_size,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        IMG_DATA_PATH,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(224, 224),
        batch_size=batch_size,
    )
    # print('data loaded')
    global model
    model = MyModel(len(train_ds.class_names))

    # train the model
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )
    history = model.fit(train_ds, validation_data=val_ds, epochs=epochs, verbose=1)

    # grade the model
    acc = history.history["accuracy"]
    val_acc = history.history["val_accuracy"]

    loss = history.history["loss"]
    val_loss = history.history["val_loss"]

    eval =  {
        "message": "Model trained successfully",
        "accuracy": acc,
        "val_accuracy": val_acc,
        "loss": loss,
        "val_loss": val_loss,
    }
    httpx.post("http://backend:8000/model/train/done", json=eval)



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

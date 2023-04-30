from model import MyModel
import tensorflow as tf
import fastapi
import services
import os
import numpy as np
import json


############ MYMODEL INIT ############

BACKEND_URL = os.getenv("BACKEND_URL")
SHARED_DATA_PATH = os.getenv("SHARED_VOLUME")
IMG_DATA_PATH = f"{SHARED_DATA_PATH}/images"

app = fastapi.FastAPI(title="TrainMyModel MyModel", version="0.1.0")
app.model = None
app.train_ds = None


############ ROUTES ############

@app.get("/")
async def root():
    return {"message": "model is running"}

# load the model from shared folder if exists
@app.get("/model/load")
async def load_model(num_classes: int):
    app.model = services.load_model(SHARED_DATA_PATH, num_classes)
    return {"message": "model loaded successfully"}

# train the model using given parameters and save it to shared folder
@app.get("/model/train", response_model=None)
async def train(batch_size: int, epochs: int, optimizer:str, loss: str,learning_rate: float, momentum: float, ):
    app.train_ds, app.val_ds = services.get_datasets(IMG_DATA_PATH, batch_size)

    app.model = MyModel(len(app.train_ds.class_names))
    services.compile_model(app.model,optimizer=optimizer, loss=loss, lr=learning_rate, momentum=momentum)
    history = services.train_model(app.model, app.train_ds, app.val_ds, epochs)

    # find the best epoch accuracy
    best_index = np.argmax(history.history["val_accuracy"])
    acc = history.history["accuracy"][best_index]
    val_acc = history.history["val_accuracy"][best_index]

    loss = history.history["loss"][best_index]
    val_loss = history.history["val_loss"][best_index]

    services.save_model(app.model, SHARED_DATA_PATH)

    eval = {
        "accuracy": acc,
        "val_accuracy": val_acc,
        "loss": loss,
        "val_loss": val_loss,
    }

    return {
        "message": "Model trained successfully",
        "train_size": len(app.train_ds.file_paths),
        "val_size": len(app.val_ds.file_paths),
        "eval": eval,
    }


@app.get("/model/delete")
async def delete_model():
    services.delete_model(SHARED_DATA_PATH)
    app.model = None
    return {"message": "Model deleted successfully"}


# predict the class of the data
@app.post("/model/predict")
async def predict(request: fastapi.Request):
    data = await request.body()
    path_to_img: str = json.loads(data)["path_to_img"]
    classes = json.loads(data)["classes"]
    classes.sort()

    if app.model is None:
        # try to load from shared volume
        app.model = services.load_model(SHARED_DATA_PATH, len(classes))
        if app.model is None:
            raise fastapi.HTTPException(status_code=400, detail="Model not trained")

    # load the image
    img = tf.keras.utils.load_img(path_to_img, target_size=(224, 224))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    predictions = app.model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    pred = {
        "message": "Prediction successful",
        "prediction": classes[np.argmax(score)],
        "confidence": 100 * np.max(score),
        "argmax": int(np.argmax(score)),
    }

    return pred

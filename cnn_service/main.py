from model import MobileNetModel
from typing import List
import tensorflow as tf
from keras import layers
import fastapi
import os
import numpy as np


app = fastapi.FastAPI()
model = None
train_ds = None

# add class and data to the model
@app.post('/model/add_class')
async def add_class(label: str, data):
    try:
        os.mkdir('data/' + label)
    except:
        pass
    for i in range(len(data)):
        # save the image to the data folder
        print(data[i].shape)

    return {"message": "Class added successfully"}

# train the model
@app.post('/model/train')
async def train(batch_size: int, epochs: int):
    # load the data from the data folder
    train_ds = tf.keras.utils.image_dataset_from_directory(
        'data',
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(224, 224),
        batch_size=batch_size
        )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        'data',
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(224, 224),
        batch_size=batch_size
        )
    
    global model
    model = MobileNetModel(len(train_ds.class_names))

    # train the model
    model.compile(optimizer='adam',
                    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                    metrics=['accuracy'])
    history = model.fit(train_ds, validation_data=val_ds, epochs=epochs, verbose=1)

    # grade the model
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    return {"message": "Model trained successfully", "accuracy": acc, "val_accuracy": val_acc, "loss": loss, "val_loss": val_loss}

# predict the class of the data
@app.post('/model/predict')
async def predict(data):
    if model is None:
        raise fastapi.HTTPException(status_code=400, detail="Model not trained")
    
    # load the image
    img = tf.keras.utils.load_img(
        data, target_size=(224, 224)
    )
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # Create a batch

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    return {"message": "Prediction successful", "class": train_ds.class_names[np.argmax(score)], "score": 100 * np.max(score)}
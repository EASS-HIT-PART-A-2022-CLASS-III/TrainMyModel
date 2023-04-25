import tensorflow as tf
from model import MyModel
import os
import shutil

def get_datasets(path: str, batch_size: int):
    return tf.keras.utils.image_dataset_from_directory(
        path,
        validation_split=0.2,
        subset="both",
        seed=123,
        image_size=(224, 224),
        batch_size=batch_size,
    ) 


def train_model(model, train_ds, validation_ds, epochs: int):
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )
    history = model.fit(train_ds, validation_data=validation_ds,
                        epochs=epochs, verbose=1)
    return history

def save_model(model, path: str):
    model.save_weights(f'{path}/model/final_model')
    shutil.make_archive(f"{path}/output/model_weights","zip", f'{path}/model')


def load_model(path: str):
    if len(os.listdir(f'{path}/model')) == 0:
        return None
    model = MyModel()
    model.load_weights(f'{path}/model/final_model')
    return model

def delete_model(path: str):
    files = os.listdir(f'{path}/model')
    if len(files) == 0:
        return None
    for file in files:
        os.remove(f'{path}/model/{file}')
    return None
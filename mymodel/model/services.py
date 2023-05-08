import tensorflow as tf
from model.model import MyModel
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

def compile_model(model,lr: float, momentum: float,optimizer: str = 'Adam', loss: str = 'Sparse Categorical Crossentropy', metrics=['accuracy'] ):

    if optimizer == "Adam":
        optimizer = tf.keras.optimizers.Adam(learning_rate=lr)
    elif optimizer == "SGD":
        optimizer = tf.keras.optimizers.SGD(learning_rate=lr, momentum=momentum)
    elif optimizer == "RMSprop":
        optimizer = tf.keras.optimizers.RMSprop(learning_rate=lr, momentum=momentum)
    elif optimizer == "Adagrad":
        optimizer = tf.keras.optimizers.Adagrad(learning_rate=lr)
    elif optimizer == "Adadelta":
        optimizer = tf.keras.optimizers.Adadelta(learning_rate=lr)
    
    if loss == "Mean Squared Error":
        loss = tf.keras.losses.MeanSquaredError()
    elif loss == "Sparse Categorical Crossentropy":
        loss = tf.keras.losses.SparseCategoricalCrossentropy()
    

    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=metrics,
    )
    

def train_model(model, train_ds, validation_ds, epochs: int):
    
    history = model.fit(
        train_ds, validation_data=validation_ds, epochs=epochs, verbose=1
    )
    return history


def save_model(model, path: str):
    model.save_weights(f"{path}/model/final_model")
    tf.keras.utils.plot_model(model.model(), to_file=f"{path}/model/vis-model.png", show_shapes=True, show_trainable=True, show_layer_names=True, expand_nested=True, show_layer_activations=True)
    save_model_archive(model, path)

def save_model_archive(model, path: str):
    shutil.make_archive(f"{path}/output/model_weights", "zip", f"{path}/model")

def load_model(path: str, num_classes: int):
    if len(os.listdir(f"{path}/model")) == 0:
        return None
    
    model = MyModel(num_classes)
    model.load_weights(f"{path}/model/final_model")
    save_model_archive(model, path)
    return model


def delete_model(path: str):
    files = os.listdir(f"{path}/model")
    if len(files) != 0:
        for file in files:
            os.remove(f"{path}/model/{file}")

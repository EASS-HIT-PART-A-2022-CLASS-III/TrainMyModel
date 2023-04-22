import tensorflow as tf


def get_datasets(path: str, batch_size: int):
    train_ds = tf.keras.utils.image_dataset_from_directory(
        path,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(224, 224),
        batch_size=batch_size,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        path,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(224, 224),
        batch_size=batch_size,
    )
    return train_ds, val_ds


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
    model.save(f'{path}/model/final_model.h5')
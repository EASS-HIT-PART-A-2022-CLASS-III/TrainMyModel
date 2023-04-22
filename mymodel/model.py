import tensorflow as tf
from tensorflow.keras import layers
import tensorflow_hub as hub
import os


class MyModel(tf.keras.Model):
    def __init__(self, num_classes):
        super(MyModel, self).__init__()

        # os.mkdir('data')

        # Create a MobileNet model with pre-trained weights
        self.resnet_v2 = tf.keras.Sequential(
            [
                hub.KerasLayer(
                    "https://tfhub.dev/google/imagenet/resnet_v2_50/classification/5"
                )
            ]
        )

        # Add additional layers on top of the pre-trained MobileNet model
        self.normalization_layer = layers.Rescaling(1.0 / 255)
        # self.global_average_pooling = tf.keras.layers.GlobalAveragePooling2D()
        self.dense1 = tf.keras.layers.Dense(128, activation="relu")
        self.dropout = tf.keras.layers.Dropout(0.5)
        self.output_layer = tf.keras.layers.Dense(num_classes, activation="softmax")

    def call(self, inputs):
        # Pass the inputs through the MobileNet model
        x = self.normalization_layer(inputs)
        x = self.resnet_v2(x)

        # Add the additional layers on top of the pre-trained MobileNet model
        # x = self.global_average_pooling(x)
        x = self.dense1(x)
        x = self.dropout(x)
        output = self.output_layer(x)

        return output

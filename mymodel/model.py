import tensorflow as tf
import tensorflow_hub as hub


class MyModel(tf.keras.Model):
    def __init__(self, num_classes):
        super(MyModel, self).__init__()

        # Create a ResNet model with pre-trained weights
        self.resnet_v2 = tf.keras.Sequential(
            [
                hub.KerasLayer(
                    "https://tfhub.dev/google/imagenet/resnet_v2_50/classification/5"
                )
            ], name="resnet_v2_50"
        )
        self.resnet_v2.trainable = False
        # Add additional layers on top of the pre-trained model
        self.normalization_layer = tf.keras.layers.Rescaling(1.0 / 255, name="MyModel_Input_Normalization")

        self.dense1 = tf.keras.layers.Dense(128, activation="relu", name="MyModel_Dense")
        self.dropout = tf.keras.layers.Dropout(0.5, name="MyModel_Dropout")

        activation = "sigmoid" if num_classes == 2 else "softmax"
        self.output_layer = tf.keras.layers.Dense(num_classes, activation=activation, name="MyModel_Output")


    def call(self, inputs):

        # Preprocess the input images
        x = self.normalization_layer(inputs)
        # Pass the inputs through resnet model
        x = self.resnet_v2(x)

        # Add the additional layers on top of the pre-trained MobileNet model
        x = self.dense1(x)
        x = self.dropout(x)
        output = self.output_layer(x)

        return output
    
    def model(self):
        x = tf.keras.layers.Input(shape=(224, 224, 3), name="MyModel_Input")
        return tf.keras.Model(inputs=[x], outputs=self.call(x), name="MyModel")


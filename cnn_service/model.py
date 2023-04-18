import tensorflow as tf
from tensorflow.keras.applications import MobileNet
from tensorflow.keras import layers
import os



class MobileNetModel(tf.keras.Model):
    def __init__(self, num_classes):
        super(MobileNetModel, self).__init__()
        
        os.mkdir('data')
    
        # Create a MobileNet model with pre-trained weights
        self.mobilenet = MobileNet(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

        # Add additional layers on top of the pre-trained MobileNet model
        normalization_layer = layers.Rescaling(1./255)
        self.global_average_pooling = tf.keras.layers.GlobalAveragePooling2D()
        self.dense1 = tf.keras.layers.Dense(128, activation='relu')
        self.dropout = tf.keras.layers.Dropout(0.5)
        self.output_layer = tf.keras.layers.Dense(num_classes, activation='softmax')

    def call(self, inputs):
        # Pass the inputs through the MobileNet model
        x = self.normalization_layer(inputs)
        x = self.mobilenet(x)

        # Add the additional layers on top of the pre-trained MobileNet model
        x = self.global_average_pooling(x)
        x = self.dense1(x)
        x = self.dropout(x)
        output = self.output_layer(x)

        return output
    
    

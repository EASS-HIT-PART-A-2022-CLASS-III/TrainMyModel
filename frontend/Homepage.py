import streamlit as st
import httpx
import os
from services import load_sidebar

######## Page Config ########

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="TrainMyModel",
    page_icon="res/logo.png",
)

######## Sidebar Config ########


   

load_sidebar()

######## Page Content ########

st.image("res/logo.png", width=200)


st.markdown(
    """
    # Train My Model

    TrainMyModel is a web app to train a *CNN* (Convolution Neural Network) deep learning model for image classification,
    It is based on the [TensorFlow](https://www.tensorflow.org/) framework, using *ResNet50* as the base model.   
    You can build your own dataset and train a model to classify images.  
      
    This app was built using *Streamlit* and *FastAPI* in Docker, and deployed using *Docker-Compose*.   
    **Final project for EASS course at HIT, 2023**.

    ### 🤖 How to use:
    1. Define your classes and upload images for each class in **My Classes** page.
    2. Choose training parameters and train the model in **Train My Model** page.
    3. Get the model's info and download the model in **My Model** page.
    4. Test the model on new images in **Predict** page.

    ### 📦 Data: 
    Both the images and the model are stored in the shared volume,  
    This way the data is saved even if the container is closed.  
    The data is stored in the following structure:

    ``` bash
    shared_volume
    ├── images
    │   ├── class1
    │   │   ├── img1.jpg
    │   │   ├── img2.jpg
    │   │   └── ...
    │   ├── class2
    │   │   ├── img1.jpg
    │   │   ├── img2.jpg
    │   │   └── ...
    │   └── ...
    └── model
        ├── model-weights.h5
        ├── model-weights.zip 
        └── model.json
    ```
    
    """
)

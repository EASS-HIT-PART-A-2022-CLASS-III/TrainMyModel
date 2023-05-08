import streamlit as st
import httpx
import os

######## Page Config ########

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="TrainMyModel",
    page_icon="res/logo.png",
)

######## Sidebar Config ########

def load_sidebar():
    res = httpx.get(f"{BACKEND_URL}/model/status")
    model_status = res.json()['model_info']['status']
    st.sidebar.title("Model status:")
    if model_status == "trained":
        st.sidebar.info("Model is Trained")
    elif model_status == "not trained":
        st.sidebar.info("Model is not Trained")
    elif model_status == "training":
        st.sidebar.info("Model is Training")
    elif model_status == "data changed":
        st.sidebar.info("Data changed, model needs to be trained again")
    st.sidebar.divider()

    _,col,_ = st.sidebar.columns([1,2,1])
    col.image("res/sidebar-logo.png")
    st.sidebar.divider()
    _,col,_ = st.sidebar.columns([1,8,1])
    col.write("©️ Built by [Matan Mizrachi](http://www.github.com/matanini), 2023")
   

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

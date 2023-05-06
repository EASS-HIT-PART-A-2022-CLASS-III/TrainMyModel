import streamlit as st
import httpx
import os


BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="TrainMyModel",
    page_icon="res/logo.png",
)

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
    _,col,_ = st.sidebar.columns([1,3,1])
    col.write("©️ Built by [Matan Mizrachi](http://www.github.com/matanini)")
   

load_sidebar()

st.image("res/logo.png", width=200)


st.markdown(
    """
    # Train My Model

    This is a web app that can be used to train a classification model.
    Using CNN deep learning model, the app can be used to train a model to classify images.
    The app is built using Streamlit and FastAPI in Docker.

    ## How to use
    1. Define your classes and upload images for each class.
    2. Train the model.
    3. Test the model.
    4. Download the model - if you want 😎.
    """
)

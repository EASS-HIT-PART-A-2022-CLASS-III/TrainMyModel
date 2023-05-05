import streamlit as st
import httpx
import os


BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="TrainMyModel",
    page_icon="🤖",
)

def load_model_status_to_sidebar():
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

load_model_status_to_sidebar()

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

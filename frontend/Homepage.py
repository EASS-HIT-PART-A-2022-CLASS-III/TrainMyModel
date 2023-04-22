import streamlit as st

SHARED_DATA_PATH = "/usr/src/shared-volume/"

st.set_page_config(
    page_title="TrainMyModel",
    page_icon=":model:",
)


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

st.sidebar.success("Select a demo above.")

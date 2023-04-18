import streamlit as st
import httpx
from fastapi import UploadFile
from PIL import Image
import os
from io import StringIO

SHARED_DATA_PATH = "/usr/src/shared-volume/"


def home():
    st.title("TrainMyModel")
    st.write("A clasification model training web app")


def test():
    st.title("Test services")
    res = httpx.get("http://backend:8001/")
    st.write("Backend response: ", res.text)
    res = httpx.get("http://ml-service:8002/")
    st.write("ML-service response: ", res.text)
    st.write("goni test")


def add_class():
    st.title("Add Class")
    st.write("Add a class to the model")
    label = st.text_input("Label")
    data = st.file_uploader("Data", type=["jpg", "png"], accept_multiple_files=True)
    if st.button("Add Class"):
        if label == "":
            st.error("Label cannot be empty")
        elif len(data) == 0:
            st.error("Data cannot be empty")
        else:
            files_dict = {}
        for i, file in enumerate(data):
            files_dict[f"file_{i}"] = (file.filename, file.file)
            # data = [UploadFile(filename=img.name, file=img, size=img.size ) for img in data]
            # for img in data:

            res = httpx.post("http://backend:8001/model/add_class", data={"label": label, "data": data})
            st.success("Class added successfully")

    # show all classes
    with st.expander("See classes"):
        res = httpx.get("http://backend:8001/model/classes")
        st.write(res.text)


def train():
    st.title("Train Model")
    st.write("Train the model")
    batch_size = st.slider("Batch Size", 1, 64, 16)
    epochs = st.slider("Epochs", 1, 50, 10)
    if st.button("Train Model"):
        # send to model service
        st.success("Model trained successfully")


def predict():
    st.title("Predict")
    st.write("Predict the class of the data")
    data = st.file_uploader("Data", type=["jpg", "png"], accept_multiple_files=True)
    if st.button("Predict"):
        if len(data) == 0:
            st.error("Data cannot be empty")
        else:
            st.success("Prediction successful")


def upload():
    st.title("Upload")
    st.write("Upload a file to the model")
    file = st.file_uploader("File", type=["jpg", "png"])
    if st.button("Upload"):
        if file.filename == "":
            st.error("File cannot be empty")
        else:
            st.success("File uploaded successfully")


def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Home", "Test services", "Add Class", "Train Model", "Predict", "Upload"])
    if selection == "Home":
        home()
    elif selection == "Test services":
        test()
    elif selection == "Add Class":
        add_class()
    elif selection == "Train Model":
        train()
    elif selection == "Predict":
        predict()
    elif selection == "Upload":
        upload()


if __name__ == "__main__":
    main()

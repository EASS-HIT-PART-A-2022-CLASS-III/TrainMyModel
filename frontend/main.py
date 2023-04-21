import streamlit as st
import httpx
from fastapi import UploadFile
from PIL import Image
import os
from io import StringIO, BytesIO

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
  

def add_class():
    if 'add_class' in st.session_state and st.session_state['add_class']:
        st.success("Class added successfully")
        st.session_state['add_class'] = False
    if 'delete_class' in st.session_state and st.session_state['delete_class']:
        st.error("Class deleted successfully")
        st.session_state['delete_class'] = False

    st.title("Model Classes")
    
    num_of_class = httpx.get("http://backend:8001/model/classes")
    num_of_class = num_of_class.json()['classes']
    # st.write(num_of_class)
    if len(num_of_class) == 0:
        st.info("No classes found")
    else:
        # Tabs for each class
        # sort the dict
        keys = list(num_of_class.keys())
        keys.sort()
        num_of_class = {k: num_of_class[k] for k in keys}

        # num_of_class = sorted(num_of_class)
        tabs = st.tabs(num_of_class)

        for i, (gold_label, img_count) in enumerate(num_of_class.items()):
            tabs[i].subheader(f"Class: {gold_label}")
            tabs[i].write(f"Number of images: {img_count}")

            if tabs[i].checkbox("Delete Class", key=f"cb_delete_class_{i}"):
                
                delete = tabs[i].button("Delete Class", key=f"delete_class_{i}")
                if delete:
                    # delete the class
                    res = httpx.post("http://backend:8001/model/classes/delete", params={"label": gold_label})
                    # st.info(f"Class {gold_label} deleted")
                    st.session_state['delete_class'] = True
                    st.experimental_rerun()

    st.markdown("""---""")
    # 
    st.write("Add a class to the model:")
    label = st.text_input("Label")
    data = st.file_uploader("Data", type=["jpg", "png"], accept_multiple_files=True)
    if st.button("Add Class"):
        if label == "":
            st.error("Label cannot be empty")
        elif len(data) == 0:
            st.error("Data cannot be empty")
        else:
            # save the images in shared volume
            os.makedirs(f"{SHARED_DATA_PATH}/images/{label}", exist_ok=True)
            for img in data:
                img_file = Image.open(img)
                img_file.save(f"{SHARED_DATA_PATH}/images/{label}/{img.name}")

            res = httpx.post("http://backend:8001/model/classes/add", params={"label": label, 'number_of_images': len(data)})
            # refresh the page
            # st.experimental_rerun()
            st.session_state['add_class'] = True
            st.experimental_rerun()



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

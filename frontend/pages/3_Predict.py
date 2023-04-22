
from PIL import Image
import numpy as np
import streamlit as st

st.set_page_config(page_title="Predict", page_icon="📈")

st.title("Predict")
st.subheader("Either upload a picture or take a picture from camera")
mode = st.radio("Select mode:", ["Upload", "Camera"])
container = st.container()
if mode == "Upload":
    container.write("Upload a picture to the model:")
    data = st.file_uploader("Data", type=["jpg", "png"], accept_multiple_files=True)
    if st.button("Upload"):
        if len(data) == 0:
            st.error("Data cannot be empty")
        else:
            st.success("File uploaded successfully")
else:
    container.write("Take a picture from camera")
    img_file_buffer = st.camera_input("")

    if img_file_buffer is not None:
        # To read image file buffer as a PIL Image:
        img = Image.open(img_file_buffer)
        st.image(img, caption="Uploaded Image.", use_column_width=True)

# st.title("Predict")
# st.write("Predict the class of the data")
# data = st.file_uploader("Data", type=["jpg", "png"], accept_multiple_files=True)
# if st.button("Predict"):
#     if len(data) == 0:
#         st.error("Data cannot be empty")
#     else:
#         st.success("Prediction successful")


# def predict_files():
#     st.title("Upload")
#     st.write("Upload a file to the model")
#     file = st.file_uploader("File", type=["jpg", "png"])
#     if st.button("Upload"):
#         if file.filename == "":
#             st.error("File cannot be empty")
#         else:
#             st.success("File uploaded successfully")

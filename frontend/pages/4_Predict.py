
from PIL import Image
import numpy as np
import streamlit as st
import httpx
import asyncio
from fastapi.responses import FileResponse

st.set_page_config(page_title="Predict", page_icon="📈")

async def make_request(data):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BACKEND_URL}/model/predict",
                           params={"data":data},
                           timeout=None)  # Set timeout to None to disable it
        return res

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
            st.write(data)
            
            st.success("File uploaded successfully")
            # res = asyncio.run(make_request(data))
            # container.write(res.json())

else:
    container.write("Take a picture from camera")
    img_file_buffer = st.camera_input("live-stream", label_visibility='hidden')

    if img_file_buffer is not None:
        # To read image file buffer as a PIL Image:
        img = Image.open(img_file_buffer)
        res = asyncio.run(make_request(img))


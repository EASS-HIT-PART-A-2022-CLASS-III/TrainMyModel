
from PIL import Image
import os
import streamlit as st
import httpx
import asyncio


BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(page_title="Predict", page_icon="✨")

async def make_request(file):
    async with httpx.AsyncClient() as client:
        files = {"file": file}
        res = await client.post(f"{BACKEND_URL}/model/predict",
                           params = files,
                           timeout=None)  # Set timeout to None to disable it
        return res

st.title("Predict")
# get model status from backend
res = httpx.get(f"{BACKEND_URL}/model/status")
model_status = res.json()

# if model_status["model_info"]["status"] == "not trained":
#     st.error("Model not trained yet")
#     st.stop()

st.subheader("Either upload a picture or take a picture from camera")
mode = st.radio("Select mode:", ["Upload", "Camera"])
container = st.container()
if mode == "Upload":
    container.write("Upload a picture to the model:")
    url = f"{BACKEND_URL}/model/predict" # replace with your FastAPI endpoint URL

    async def send_request(file):
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files={"file": file})
        return response

    # create a Streamlit file uploader
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    # if an image is uploaded, send the request
    if uploaded_file is not None:
        response = asyncio.run(send_request(uploaded_file))
        # do something with the response
        # st.write("Response status:", response.status_code)
        st.write("Response text:", response)
#     def send_request(data):
#         with httpx.Client() as client:
#             response = client.post(f"{BACKEND_URL}/model/predict", files=data)
#         return response

# # create a Streamlit file uploader
#     uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

#     # if an image is uploaded, send the request
#     if uploaded_file is not None:
#         data = {"file": uploaded_file}
#         response = send_request(data)
#         # do something with the response
#         st.write("Response status:", response.status_code)
#         st.write("Response text:", response.text)
    # data = st.file_uploader("Data", type=["jpg", "png"], accept_multiple_files=False)

    # if st.button("Upload"):
    #     if data is None:
    #         st.error("Data cannot be empty")
    #     else:
    #         # img = Image.open(data)
    #         res = asyncio.run(make_request(data.filename))
    #         st.success(res.text)


else:
    container.write("Take a picture from camera")
    img_file_buffer = st.camera_input("live-stream", label_visibility='hidden')

    if img_file_buffer is not None:
        # To read image file buffer as a PIL Image:
        img = Image.open(img_file_buffer)
        res = asyncio.run(make_request(img))


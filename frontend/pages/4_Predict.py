from PIL import Image
import os
import streamlit as st
import httpx
import asyncio
import io
import base64
from services import load_sidebar

######## Page Config ########

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="Predict",
    page_icon="res/logo.png"
)

colors = ["blue", "green", "orange", "red", "violet"]

######## Sidebar Config ########

load_sidebar()

######## Helper functions ########

def process_image_before_send(file):
    image = Image.open(file)
    image_bytes = io.BytesIO()
    format = 'png'
    image.save(image_bytes, format=format)
    content = base64.b64encode(image_bytes.getvalue())
    img = {'img':content.decode(), 'filename':file.name}
    return img

async def send_predict_request(file):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/model/predict", json={"images": [file], 'label':''}, timeout=None
        )
    return response

def fill_results(new_sample, response):
    results.subheader("Prediction results:")
    body = response.json()
    argmax = int(body["argmax"])
    prediction = body["prediction"]
    confidence = body["confidence"]
    col1, col2 = results.columns(2)
    col1.markdown("<br><br>", unsafe_allow_html=True)
    sep = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    col1.markdown(
        f"""
        ### **Prediction**:{sep}:{colors[argmax%len(colors)]}[{prediction}]
        #### **Confidence**:{sep}:{colors[argmax%len(colors)]}[{str(confidence)[:5]}]
    """
    )
    img = Image.open(new_sample)
    img = img.resize((224, 224))
    col2.image(
        img,
        caption=f"Detected {prediction} in image",
        use_column_width=True,
    )
    expander = results.expander("Response JSON")
    expander.json(body)


######## Page Content ########

st.title("Predict")

# get model status from backend
model_status = httpx.get(f"{BACKEND_URL}/model/status").json()

if model_status["model_info"]["status"] == "not trained":
    st.error("Your Model is not trained yet")
    st.write("Go to the train page to train it 🚂")
    st.stop()

st.subheader("Either upload a picture or take a picture from camera")
st.write("Be advised that the first prediction will take a while, as the model needs to be loaded.")
mode = st.radio("Select mode:", ["Upload", "Camera"])
container = st.container()
st.divider()
results = st.container()


if mode == "Upload":
    container.write("Upload a picture to the model:")
    # create a Streamlit file uploader
    new_sample = container.file_uploader(
        "Choose an image...", type=["jpg", "jpeg", "png"]
    )
    if container.button("Upload"):
        if new_sample is not None:
            with st.spinner("Please wait, predicting..."):
                to_pred = process_image_before_send(new_sample)
                response = asyncio.run(send_predict_request(to_pred))
            fill_results(new_sample, response)


else:
    container.write("Take a picture from camera")
    new_sample = container.camera_input("live-stream", label_visibility="hidden")
    if container.button("Upload"):
        if new_sample is not None:
            with st.spinner("Please wait, predicting..."):
                to_pred = process_image_before_send(new_sample)
                response = asyncio.run(send_predict_request(to_pred))
            fill_results(new_sample, response)


from PIL import Image
import os
import streamlit as st
import httpx
import asyncio
import io
import base64

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(page_title="Predict", page_icon="res/logo.png")

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

color = ["blue", "green", "orange", "red", "violet"]

def process_image_before_send(file):
    image = Image.open(file)
    image_bytes = io.BytesIO()
    format = 'png'
    image.save(image_bytes, format=format)
    content = base64.b64encode(image_bytes.getvalue())
    img = {'img':content.decode(), 'filename':file.name}
    return img

async def send_request(file):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/model/predict", json={"images": [file], 'label':''}, timeout=None
        )
    return response


st.title("Predict")
# get model status from backend
res = httpx.get(f"{BACKEND_URL}/model/status")
model_status = res.json()

st.subheader("Either upload a picture or take a picture from camera")
st.write("Be advised that the first prediction will take a while, as the model needs to be loaded.")
mode = st.radio("Select mode:", ["Upload", "Camera"])
container = st.container()
st.divider()
results = st.container()


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
        ### **Prediction**:{sep}:{color[argmax%len(color)]}[{prediction}]
        #### **Confidence**:{sep}:{color[argmax%len(color)]}[{str(confidence)[:5]}]
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
                response = asyncio.run(send_request(to_pred))
            fill_results(new_sample, response)


else:
    container.write("Take a picture from camera")
    new_sample = container.camera_input("live-stream", label_visibility="hidden")
    if container.button("Upload"):
        if new_sample is not None:
            with st.spinner("Please wait, predicting..."):
                to_pred = process_image_before_send(new_sample)
                response = asyncio.run(send_request(to_pred))
            fill_results(new_sample, response)


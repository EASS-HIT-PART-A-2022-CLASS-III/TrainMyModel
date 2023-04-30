from PIL import Image
import os
import streamlit as st
import httpx
import asyncio


BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(page_title="Predict", page_icon="✨")
color = ["blue", "green", "orange", "red", "violet"]


async def send_request(file):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/model/predict", files={"file": file}, timeout=None
        )
    return response


st.title("Predict")
# get model status from backend
res = httpx.get(f"{BACKEND_URL}/model/status")
model_status = res.json()

st.subheader("Either upload a picture or take a picture from camera")
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
        ### **Prediction**:{sep}:{color[argmax]}[{prediction}]
        #### **Confidence**:{sep}:{color[argmax]}[{str(confidence)[:5]}]
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
        # if an image is uploaded, send the request
        if new_sample is not None:
            response = asyncio.run(send_request(new_sample))
            fill_results(new_sample, response)


else:
    container.write("Take a picture from camera")
    new_sample = container.camera_input("live-stream", label_visibility="hidden")
    if container.button("Upload"):
        if new_sample is not None:
            # To read image file buffer as a PIL Image:
            # img = Image.open(new_sample)
            response = asyncio.run(send_request(new_sample))
            fill_results(new_sample, response)
            # img = Image.open(new_sample)
            # results.image(img, caption="Uploaded Image", use_column_width=True)
            # results.write("Prediction: " + response.json()["class"])
            # results.write("Probability: " + str(response.json()["score"]))
            # expander = results.expander("Response JSON")
            # expander.json(response.json())


# results.subheader("Prediction results:")

# img = Image.open(new_sample)
# results.image(img, caption="Uploaded Image", use_column_width=True)
# results.write("Prediction: " + response.json()["class"])
# results.write("Probability: " + str(response.json()["score"]))

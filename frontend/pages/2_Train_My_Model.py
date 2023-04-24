import os
import streamlit as st
import httpx
import time
import asyncio

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(page_title="Train My Model", page_icon="🤖")

model_status = httpx.get(f"http://{BACKEND_URL}/model/status").json()
if model_status["model_info"]["status"] == "trained":
    st.warning("Model already trained")
    st.write("Check model page for info")
    st.stop()
if model_status["model_info"]["status"] == "training":
    st.warning("Model is training, be patient")
    st.write("Check model page for info")
    st.stop()

st.title("Train Model")
st.write("Choose the train parameters:")
batch_size = st.slider("Batch Size", 10, 64, 16)
epochs = st.slider("Epochs", 5, 50, 5)
train_btn = st.button("Train Model")
results = st.container()


async def make_request():
    async with httpx.AsyncClient() as client:
        res = await client.post(f"http://{BACKEND_URL}/model/train",
                           params={"batch_size": batch_size, "epochs": epochs},
                           timeout=None)  # Set timeout to None to disable it
        return res  # Close the connection immediately
        

if train_btn:
    with st.spinner("Model Training in Progress"):
        res = asyncio.run(make_request())
    
    results.write(res.text)
    results.write("Check model page for info")

# if 
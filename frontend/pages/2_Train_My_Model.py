import os
import streamlit as st
import httpx
import asyncio
from services import load_sidebar

######## Page Config ########

BACKEND_URL = os.getenv("BACKEND_URL")
st.set_page_config(
    page_title="Train My Model", 
    page_icon="res/logo.png"
)

######## Sidebar Config ########

load_sidebar()

######## Helper functions ########

async def make_train_request():
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BACKEND_URL}/model/train",
            params={
                "batch_size": batch_size,
                "epochs": epochs,
                "optimizer": optimizer,
                "learning_rate": learning_rate,
                "momentum": momentum,
                "loss": loss,
            },
            timeout=None,
        )
        return res


######## Page Content ########

model_status = httpx.get(f"{BACKEND_URL}/model/status").json()
if model_status["model_info"]["status"] == "trained":
    st.error("My Model is already trained 🤷‍♂️")
    st.markdown("Check **My Model** page for more information")
    st.stop()
if model_status["model_info"]["status"] == "training":
    st.warning("My Model is training, be patient 🙏")
    st.markdown("Check **My Model** page for more information")
    st.stop()

st.title("Train Model")
st.write("Choose the train parameters:")
batch_size = st.slider("Batch Size", 10, 100, 16)
epochs = st.slider("Epochs", 5, 25, 10)
optimizer = st.selectbox("Optimizer", ["Adam", "SGD", "RMSprop", "Adagrad", "Adadelta"])

momentum = 0
learning_rate = st.selectbox(
    "Learning Rate", [0.1, 0.01, 0.001, 0.0001, 0.00001], index=2
)
if optimizer in ["SGD", "RMSprop"]:
    momentum = st.number_input(
        "Momentum", min_value=0.0, max_value=1.0, value=0.9, step=0.1
    )

loss = st.selectbox(
    "Loss",
    [
        "Sparse Categorical Crossentropy",
        "Mean Squared Error",
    ],
)

st.write("Click the button below to start training")

train_btn = st.button("Train Model")
results = st.container()

if train_btn:
    with st.spinner("Model Training in Progress"):
        res = asyncio.run(make_train_request())

    if res.status_code != 200:
        st.error(f"Error: {res.json()['detail']}")
        st.stop()

    res = res.json()
    results.success(res["message"])
    results.write("Check model page for info")

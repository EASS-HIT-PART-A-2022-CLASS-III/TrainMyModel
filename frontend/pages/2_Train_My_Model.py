
import streamlit as st
import httpx

st.set_page_config(page_title="Train My Model", page_icon="📈")

st.title("Train Model")
st.write("Classes: ")
batch_size = st.slider("Batch Size", 1, 64, 16)
epochs = st.slider("Epochs", 1, 50, 10)

if st.button("Train Model"):
    # send to model service
    res = httpx.post(
        "http://backend:8001/model/train",
        params={"batch_size": batch_size, "epochs": epochs},
    )
    st.success(res.json())
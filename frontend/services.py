import streamlit as st
import httpx
import os

BACKEND_URL = os.getenv("BACKEND_URL")

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
    _,col,_ = st.sidebar.columns([1,8,1])
    col.write("©️ Built by [Matan Mizrachi](http://www.github.com/matanini), 2023")
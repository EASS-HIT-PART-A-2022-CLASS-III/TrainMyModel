import streamlit as st
import httpx

st.set_page_config(page_title="My Model", page_icon="🤖")

st.title("My Model")

status = httpx.get("http://backend:8001/model/status").json()

# st.write(status)
if status["model_info"]["status"] == "not trained":
    st.write("Model is not trained")
elif status["model_info"]["status"] == "training":
    st.write("Model is training")
else:
    st.write("Model is trained")
    st.write(status)


import streamlit as st
import httpx
import os
import shutil

BACKEND_URL = os.getenv("BACKEND_URL")
SHARED_DATA_PATH = os.getenv("SHARED_VOLUME")

st.set_page_config(page_title="My Model", page_icon="🤖")

st.title("My Model")

if "model deleted" in st.session_state and st.session_state["model deleted"]:
    st.success("Model deleted successfully")
    st.session_state["model deleted"] = False

status = httpx.get(f"{BACKEND_URL}/model/status").json()

# st.write(status)
if status["model_info"]["status"] == "not trained":
    st.write("Model is not trained")
    st.write("Go to the train page to train it")
elif status["model_info"]["status"] == "training":
    st.write("Model is training")
else:
    st.markdown("**Model is trained!**")
    st.markdown("Now you can predict with it or train it again!")
    st.divider()
    st.markdown("""
    **Download the model**  
    The zip file contains the weights, index and checkpoint.
    To load it in your code, define the class and load the weights:
    ```
    model = MyModel()
    model.load_weights(f'path/to/model/final_model')
    ```
    
    """)

    with open(f'{SHARED_DATA_PATH}/output/model_weights.zip','rb') as file:
        download_btn = st.download_button(label="Download weights",
                            data=file,
                            file_name="model_weights.zip"
                          )

    st.divider()
    expander = st.expander("More Info")
    expander.write(status)
    st.divider()
    st.warning("Training again will reset the model")
    if st.button("I want to train again"):
        res = httpx.get(f"{BACKEND_URL}/model/delete")
        st.session_state["model deleted"] = True
        st.experimental_rerun()
        




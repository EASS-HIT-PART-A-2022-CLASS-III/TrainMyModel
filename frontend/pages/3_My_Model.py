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
    st.error("Model is not trained")
    st.write("Go to the train page to train it 🚂")
    st.stop()
elif status["model_info"]["status"] == "training":
    st.warning("Model is training")
    st.write("Be patient, it will be ready soon 😊")
else:
    st.markdown("**Model is trained!**")
    st.markdown("Now you can predict with it or train it again!")
    st.divider()
    st.markdown(
        """
    ##### **Download the model**  
    The downloaded zip file contains the weights, index and checkpoints of the trained model.  
    In order to load it in your code, follow these steps:  
    1. Download and unzip the files
    2. Define ```MyModel()``` class in your code
    3. Load the weights using tensorflow
      
    Example:
    ```
    model = MyModel()
    model.load_weights(f'path/to/model/final_model')
    ```
    """
    )

    with open(f"{SHARED_DATA_PATH}/output/model_weights.zip", "rb") as file:
        download_btn = st.download_button(
            label="Download weights", data=file, file_name="model_weights.zip"
        )

    st.divider()
    st.markdown("##### **Model information:**")
    expander = st.expander("Open for info")
    expander.write(status)
    st.divider()
    st.warning("Training again will reset the model")
    if st.button("I want to train again"):
        res = httpx.get(f"{BACKEND_URL}/model/delete")
        st.session_state["model deleted"] = True
        st.experimental_rerun()

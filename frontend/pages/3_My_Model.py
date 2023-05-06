import streamlit as st
import httpx
import os
import io
from PIL import Image
import base64

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(page_title="My Model", page_icon="res/logo.png")

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
    st.stop()
elif status["model_info"]["status"] == "data changed":
    st.warning("Data changed, model needs to be trained again")
    st.write("Go to the train page to train it 🚂")
    st.stop()
else:
    st.success("Model is **trained** and ready to use 🎉")
    st.markdown(
        """           
        You can start using it in the **predict** page to predict new images.  
        You can see the model summary, architecture and training information below.  
        In addition, you can download the model and use it in your own projects.  
        Examples of how to use it are available in the **How to use it** section.  
        
        """)
    
    st.divider()
    st.markdown("""
    ### **Model information**
    Here you can find information about the trained model.
    """)
    st.markdown("""
    ##### 📝 **Model summary:**
    Overview of the model layers and parameters.  
    See [Tensorflow docs](https://www.tensorflow.org/api_docs/python/tf/keras/Model#summary) for more info.    
    """)
    summ_expander = st.expander("Open for more info")
    summ_expander.code(status["model_info"]["summary"])

    st.markdown("""
    ##### 👷‍♂️ **Model architecture:**
    Model architecture diagram.  
    You can see the model layers and how they are connected, as well as the input and output shapes.  
    Names of the layers are also shown, together with if trainable **(T)** or not **(NT)**.  
    See [Tensorflow docs](https://www.tensorflow.org/api_docs/python/tf/keras/Model#plot_model) for more info.  
    """)

    arch_expander = st.expander("Open for more info")
    # get the image from backend
    res = httpx.get(f"{BACKEND_URL}/model/architecture")
    image = Image.open(io.BytesIO(base64.b64decode(res.content)), formats=["png"])
    arch_expander.image(image)

    st.markdown("""
    ##### 🎒 **Training information:**
    Information about the training process.  
    You can see the data and training parameters, as well as the training and validation metrics.  
    
    """)
    info_expander = st.expander("Open for more info")
    more_info = status.copy()
    more_info['model_info'].pop('summary')
    info_expander.write(more_info)

    st.divider()
    st.markdown("### **How to use it**")
    st.markdown(
        """
    ##### 1. 💻 **Download the model**  
    The downloaded zip file contains the weights, index and checkpoints of the trained model.  
    In order to load it in your code, follow these steps:  
    1. Download and unzip the files
    2. Define ```MyModel()``` class in your code
    3. Load the weights using tensorflow
      
    Example:
    ```python
    model = MyModel(num_class=3)
    model.load_weights('path/to/model/final_model')
    ```
    """
    )

    st.markdown("##### 2. 📝 **MyModel() code**")
    st.code(
        """
import tensorflow as tf
from tensorflow.keras import layers
import tensorflow_hub as hub

class MyModel(tf.keras.Model):
    def __init__(self, num_classes):
        super(MyModel, self).__init__()
        # we use resnet as base
        resnet_url = "https://tfhub.dev/google/imagenet/resnet_v2_50/classification/5"
        self.resnet_v2 = tf.keras.Sequential([hub.KerasLayer(resnet_url)], name="resnet_v2_50")
        self.resnet_v2.trainable = False

        # our layers
        self.normalization_layer = tf.keras.layers.Rescaling(1.0 / 255, name="MyModel_Input_Normalization")
        self.dense = tf.keras.layers.Dense(128, activation="relu", name="MyModel_Dense")
        self.dropout = tf.keras.layers.Dropout(0.5, name="MyModel_Dropout")
        activation = "sigmoid" if num_classes == 2 else "softmax"
        self.output_layer = tf.keras.layers.Dense(num_classes, activation=activation, name="MyModel_Output")

    def call(self, input):
        x = self.normalization_layer(input)
        x = self.resnet_v2(x)
        x = self.dense(x)
        x = self.dropout(x)
        output = self.output_layer(x)
        return output
        """)

    # Get the model weights from backend
    res = httpx.get(f"{BACKEND_URL}/model/download")
    file = io.BytesIO(res.content)
    
    download_btn = st.download_button(
            label="Download weights", data=file, file_name="model_weights.zip"
        )



    st.divider()
    st.markdown("##### **Reset the model**")
    st.markdown(
        """
    If you wish to reset the model and train it again, click the button below.  
    **This will delete only the model, and not the classes**.

    """
    )
    st.warning("This is an irreversible action")
    if st.checkbox("I understand the consequences"):
        if st.button("Reset my model"):
            res = httpx.get(f"{BACKEND_URL}/model/delete")
            st.session_state["model deleted"] = True
            st.experimental_rerun()

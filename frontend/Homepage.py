import streamlit as st

SHARED_DATA_PATH = "/usr/src/shared-volume/"

st.set_page_config(
    page_title="TrainMyModel",
    page_icon=":model:",
)


st.markdown(
    """
    # Train My Model

    This is a web app that can be used to train a classification model.
    Using CNN deep learning model, the app can be used to train a model to classify images.
    The app is built using Streamlit and FastAPI in Docker.

    ## How to use
    1. Define your classes and upload images for each class.
    2. Train the model.
    3. Test the model.
    4. Download the model - if you want 😎.
    """
)

st.sidebar.success("Select a demo above.")
# def test():
#     st.title("Test services")
#     res = httpx.get("http://backend:8001/")
#     st.write("Backend response: ", res.text)
#     res = httpx.get("http://mymodel:8002/")
#     st.write("mymodel response: ", res.text)


# def add_class():
#     if "add_class" in st.session_state and st.session_state["add_class"]:
#         st.success("Class added successfully")
#         st.session_state["add_class"] = False
#     if "delete_class" in st.session_state and st.session_state["delete_class"]:
#         st.error("Class deleted successfully")
#         st.session_state["delete_class"] = False
#     if "edit_class" in st.session_state and st.session_state["edit_class"]:
#         st.success("Class edited successfully")
#         st.session_state["edit_class"] = False

#     st.title("Model Classes")

#     all_classes = httpx.get("http://backend:8001/model/classes")
#     all_classes = all_classes.json()["classes"]

#     if len(all_classes) == 0:
#         st.info("No classes found")

#     else:
#         # Show the classes in tabs
#         # sort the dict
#         keys = list(all_classes.keys())
#         keys.sort()
#         all_classes = {k: all_classes[k] for k in keys}

#         # all_classes = sorted(all_classes)
#         tabs = st.tabs(all_classes)

#         for i, (gold_label, img_count) in enumerate(all_classes.items()):
#             tabs[i].subheader(f"Class: {gold_label}")
#             tabs[i].subheader(f"Number of images: {img_count}")

#             edit_btn = tabs[i].checkbox("Edit Class label", key=f"edit_class_{i}")
#             if edit_btn:
#                 newlabel = tabs[i].text_input("New Label", value=gold_label)
#                 if tabs[i].button("Save new label", key=f"save_new_label_{i}"):
#                     # edit the class
#                     res = httpx.post(
#                         "http://backend:8001/model/classes/update",
#                         params={"oldlabel": gold_label, "newlabel": newlabel},
#                     )
#                     st.session_state["edit_class"] = True
#                     st.experimental_rerun()

#             delete_btn = tabs[i].button("Delete Class", key=f"delete_class_{i}")
#             if delete_btn:
#                 # delete the class
#                 res = httpx.post(
#                     "http://backend:8001/model/classes/delete",
#                     params={"label": gold_label},
#                 )
#                 st.session_state["delete_class"] = True
#                 st.experimental_rerun()

#     st.divider()
#     #
#     st.write("Add a class to the model:")
#     label = st.text_input("Label")
#     data = st.file_uploader("Data", type=["jpg", "png"], accept_multiple_files=True)
#     if st.button("Add Class"):
#         if label == "":
#             st.error("Label cannot be empty")
#         elif len(data) == 0:
#             st.error("Data cannot be empty")
#         else:
#             # save the images in shared volume
#             os.makedirs(f"{SHARED_DATA_PATH}/images/{label}", exist_ok=True)
#             for img in data:
#                 img_file = Image.open(img)
#                 img_file.save(f"{SHARED_DATA_PATH}/images/{label}/{img.name}")

#             res = httpx.post(
#                 "http://backend:8001/model/classes/add",
#                 params={"label": label, "number_of_images": len(data)},
#             )
#             # refresh the page
#             # st.experimental_rerun()
#             data.clear()
#             st.session_state["add_class"] = True

#             st.experimental_rerun()


# def train():
#     st.title("Train Model")
#     st.write("Classes: ")
#     batch_size = st.slider("Batch Size", 1, 64, 16)
#     epochs = st.slider("Epochs", 1, 50, 10)

#     if st.button("Train Model"):
#         # send to model service
#         res = httpx.post(
#             "http://backend:8001/model/train",
#             params={"batch_size": batch_size, "epochs": epochs},
#         )
#         st.success(res.json())


# def predict_live():
#     from PIL import Image
#     import numpy as np

#     img_file_buffer = st.camera_input("Take a picture")

#     if img_file_buffer is not None:
#         # To read image file buffer as a PIL Image:
#         img = Image.open(img_file_buffer)
#         st.image(img, caption="Uploaded Image.", use_column_width=True)
#     # st.title("Predict")
#     # st.write("Predict the class of the data")
#     # data = st.file_uploader("Data", type=["jpg", "png"], accept_multiple_files=True)
#     # if st.button("Predict"):
#     #     if len(data) == 0:
#     #         st.error("Data cannot be empty")
#     #     else:
#     #         st.success("Prediction successful")


# def predict_files():
#     st.title("Upload")
#     st.write("Upload a file to the model")
#     file = st.file_uploader("File", type=["jpg", "png"])
#     if st.button("Upload"):
#         if file.filename == "":
#             st.error("File cannot be empty")
#         else:
#             st.success("File uploaded successfully")


# def main():
#     st.sidebar.title("Navigation")
#     selection = st.sidebar.radio(
#         "Go to",
#         ["Home", "Test services", "Add Class", "Train Model", "Live predict", "Predict Images"],
#     )
#     if selection == "Home":
#         home()
#     elif selection == "Test services":
#         test()
#     elif selection == "Add Class":
#         add_class()
#     elif selection == "Train Model":
#         train()
#     elif selection == "Live predict":
#         predict_live()
#     elif selection == "Predict Images":
#         predict_files()


# if __name__ == "__main__":
#     main()

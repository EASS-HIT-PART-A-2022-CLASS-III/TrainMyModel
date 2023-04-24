import streamlit as st
import httpx
import os
from PIL import Image

SHARED_DATA_PATH = "/usr/src/shared-volume/"

st.set_page_config(page_title="My Classes", page_icon="")
st.title("Model Classes")

if "add_class" in st.session_state and st.session_state["add_class"]:
    st.success("Class added successfully")
    st.session_state["add_class"] = False
if "delete_class" in st.session_state and st.session_state["delete_class"]:
    st.error("Class deleted successfully")
    st.session_state["delete_class"] = False
if "edit_class" in st.session_state and st.session_state["edit_class"]:
    st.success("Class edited successfully")
    st.session_state["edit_class"] = False


all_classes = httpx.get("http://backend:8001/model/classes")
all_classes = all_classes.json()

if len(all_classes) == 0:
    st.info("No classes found")

else:
    # Show the classes in tabs
    # sort the dict
    keys = list(all_classes.keys())
    keys.sort()
    all_classes = {k: all_classes[k] for k in keys}

    # all_classes = sorted(all_classes)
    tabs = st.tabs(all_classes)

    for i, (gold_label, img_count) in enumerate(all_classes.items()):
        tabs[i].subheader(f"Class: {gold_label}")
        tabs[i].subheader(f"Number of images: {img_count}")

        edit_btn = tabs[i].checkbox("Edit Class label", key=f"edit_class_{i}")
        if edit_btn:
            newlabel = tabs[i].text_input("New Label", value=gold_label)
            if tabs[i].button("Save new label", key=f"save_new_label_{i}"):
                # edit the class
                res = httpx.post(
                    "http://backend:8001/model/classes/update",
                    params={"oldlabel": gold_label, "newlabel": newlabel},
                )
                st.session_state["edit_class"] = True
                st.experimental_rerun()

        delete_btn = tabs[i].button("Delete Class", key=f"delete_class_{i}")
        if delete_btn:
            # delete the class
            res = httpx.post(
                "http://backend:8001/model/classes/delete",
                params={"label": gold_label},
            )
            st.session_state["delete_class"] = True
            st.experimental_rerun()

st.divider()
#
st.write("Add a class to the model:")
label = st.text_input("Label")
data = st.file_uploader("Data", type=["jpg", "png"], accept_multiple_files=True)
if st.button("Add Class"):
    if label == "":
        st.error("Label cannot be empty")
    elif len(data) == 0:
        st.error("Data cannot be empty")
    else:
        # save the images in shared volume
        os.makedirs(f"{SHARED_DATA_PATH}/images/{label}", exist_ok=True)
        for img in data:
            img_file = Image.open(img)
            img_file.save(f"{SHARED_DATA_PATH}/images/{label}/{img.name}")

        res = httpx.post(
            "http://backend:8001/model/classes/add",
            params={"label": label, "number_of_images": len(data)},
        )
        # refresh the page
        # st.experimental_rerun()
        data.clear()
        st.session_state["add_class"] = True

        st.experimental_rerun()
import streamlit as st
import httpx
import os
import asyncio
from PIL import Image
import io
import base64
from services import load_sidebar

######## Page Config ########

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="My Classes",
    page_icon="res/logo.png"
)

colors = ["blue", "green", "orange", "red", "violet"]

######## Sidebar Config ########

load_sidebar()

######## Helper functions ########

async def get_images(gold_label):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/classes/get_images/{gold_label}",
        )
    return response

async def send_delete_request(gold_label):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/classes/delete",
            params={"label": gold_label},
        )
    return response

async def send_files_async(files_to_send, label):
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/classes/add", json={'label':label, 'images' :files_to_send}, timeout=None
        )

    return response

def process_images_before_send(files):
    files_to_send = []
    for file in files:
        image = Image.open(file)
        image_bytes = io.BytesIO()
        format = 'png'
        image.save(image_bytes, format=format)
        content = base64.b64encode(image_bytes.getvalue())
        img = {'img':content.decode(), 'filename':file.name}
        files_to_send.append(img)
    return files_to_send

def process_images_from_backend(img_list):
    for img in img_list:
        img['img'] = base64.b64decode(img['img'].encode())
        img['img'] = io.BytesIO(img['img'])
        img['img'] = Image.open(img['img'])
    return img_list


######## Page Content ########

st.title("Model Classes")

if "add_class" in st.session_state and st.session_state["add_class"]:
    st.success("Class added successfully")
    st.session_state["add_class"] = False
elif "delete_class" in st.session_state and st.session_state["delete_class"]:
    st.error("Class deleted successfully")
    st.session_state["delete_class"] = False
elif "edit_class" in st.session_state and st.session_state["edit_class"]:
    st.success("Class edited successfully")
    st.session_state["edit_class"] = False
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0
if "bad_request" in st.session_state and st.session_state["bad_request"]:
    st.error("Something went wrong")
    st.session_state["bad_request"] = False

all_classes = httpx.get(f"{BACKEND_URL}/classes")
all_classes = all_classes.json()

if len(all_classes) == 0:
    st.info("No classes found")

else:
    # sort the dict
    all_classes = sorted(all_classes, key=lambda x: x["name"])

    # Show the classes in tabs
    tabs = st.tabs([data_class["name"] for data_class in all_classes])

    for i, data_class in enumerate(all_classes):
        gold_label = data_class["name"]
        img_count = data_class["samples"]
        _, col1, col2, _ = tabs[i].columns(4)
        with col1:
            st.markdown("#### **Class:**")
            st.markdown("#### **Samples:**")

        with col2:
            st.markdown(f"#### :{colors[i%len(colors)]}[{gold_label}]")
            st.markdown(f"#### :{colors[i%len(colors)]}[{img_count}]")

        tabs[i].markdown("    ")
        edit_btn = tabs[i].checkbox("Edit Class", key=f"edit_class_{i}")
        if edit_btn:
            cols = tabs[i].columns(2)
            with cols[0]:
                newlabel = st.text_input("New Label", value=gold_label)
                if st.button("Save new label", key=f"save_new_label_{i}"):
                    # edit the class
                    res = httpx.post(
                        f"{BACKEND_URL}/classes/update",
                        params={"oldlabel": gold_label, "newlabel": newlabel},
                    )
                    st.session_state["edit_class"] = True
                    st.experimental_rerun()
            with cols[1]:
                st.write("")
                st.warning("Deleting the class is irreversible")
                delete_btn = st.button("Delete Class", key=f"delete_class_{i}")
                if delete_btn:
                    # delete the class
                    res = asyncio.run(send_delete_request(gold_label))
                    st.session_state["delete_class"] = True
                    st.experimental_rerun()

        img_samples = tabs[i].expander("Image samples")
        # get the images from backend
        response = asyncio.run(get_images(gold_label))

        if response.status_code == 200:
            response = response.json()
            img_list = process_images_from_backend(response['images'])
            cols = img_samples.columns(3)
            for j, col in enumerate(cols):
                with col:
                    st.image(img_list[j]['img'], caption=img_list[j]['filename'], use_column_width=True)
        else:
            st.error("Something went wrong")
            st.write(response.text)




st.divider()

st.write("Add a class to the model:")
label = st.text_input("Label")
data = st.file_uploader("Data", type=["jpg", "png"], accept_multiple_files=True, key=st.session_state["uploader_key"])
if st.button("Add Class"):
    if label == "":
        st.error("Label cannot be empty")
    elif len(data) == 0:
        st.error("Data cannot be empty")
    else:
        # convert the files to base64
        with st.spinner(f"Standby, sending {len(data)} images of class {label}"):
            files_to_send = process_images_before_send(data)
            # send the request to backend
            result = asyncio.run(send_files_async(files_to_send, label))

        if result.status_code == 200:
            st.session_state["uploader_key"] += 1
            st.session_state["add_class"] = True           
        if result.status_code == 500:
            st.session_state["bad_request"] = True
        # refresh the page
        st.experimental_rerun()

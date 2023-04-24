
import streamlit as st
import httpx
import time
import asyncio

st.set_page_config(page_title="Train My Model", page_icon="🤖")

st.title("Train Model")
st.write("Choose the train parameters:")
batch_size = st.slider("Batch Size", 10, 64, 16)
epochs = st.slider("Epochs", 5, 50, 5)
train_btn = st.button("Train Model")
results = st.container()


async def make_request():
    async with httpx.AsyncClient() as client:
        await client.post("http://backend:8001/model/train",
                           params={"batch_size": batch_size, "epochs": epochs},
                           timeout=None)  # Set timeout to None to disable it
        await client.aclose()  # Close the connection immediately
        

if train_btn:
    asyncio.run(make_request())
    
    results.write("Model started to train")
    results.write("Check model page for info")


# if train_btn:
#     res = httpx.post("http://backend:8001/model/train",
#                         params={"batch_size": batch_size, "epochs": epochs},
#     )
#     results.write(res.text)
#     results.write("Model started to train")
#     results.write("Check model page for info")



# async def train_model():
#     # async with httpx.AsyncClient() as client:
#     res = await httpx.post(
#             "http://backend:8001/model/train",
#             params={"batch_size": batch_size, "epochs": epochs},
#             timeout=None,
#         )
#     # return res

# if train_btn:
#     # send to model service
#     try:
#         with st.spinner("Model Training in Progress"):
#             asyncio.run(train_model())
#     except Exception as e:
#             results.error("Error: "+ str(e))
#             # results.write(str(e))
#     finally:
#             res = httpx.get("http://backend:8001/model/evaluate")
#             if res.status_code == 200:
#                 results.subheader("Model Trained Successfully")
#                 results.success("Results: " + res.text)
#             else:
#                 results.subheader("Model Training Failed")
#                 results.error("Error: "+ res.text)
                

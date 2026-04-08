import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Video Forgery Detection System", layout="wide")

st.title("Video Forgery Detection System")
st.write("Upload a video file and check whether it may be forged.")

st.subheader("1. Upload video")
uploaded_file = st.file_uploader(
    "Choose a video",
    type=["mp4", "avi", "mov", "mkv"]
)

if uploaded_file is not None:
    st.success(f"Selected file: {uploaded_file.name}")

    if st.button("Analyze Video"):
        with st.spinner("Uploading and analyzing..."):
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type or "video/mp4"
                )
            }

            response = requests.post(f"{BACKEND_URL}/predict", files=files)

            if response.status_code == 200:
                data = response.json()
                st.subheader("2. Prediction result")
                col1, col2, col3 = st.columns(3)
                col1.metric("Label", data["label"])
                col2.metric("Confidence", f"{data['confidence']:.2f}")
                col3.metric("Frames analyzed", data["frames_analyzed"])
                st.json(data)
            else:
                st.error("Prediction failed.")

st.subheader("3. Previous analyses")
if st.button("Load History"):
    response = requests.get(f"{BACKEND_URL}/history")
    if response.status_code == 200:
        history = response.json()
        if history:
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No history found.")
    else:
        st.error("Could not load history.")

import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Video Forgery Detection System", layout="wide")

DB_PATH = "detections.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        label TEXT NOT NULL,
        confidence REAL NOT NULL,
        frames_analyzed INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def fake_model_prediction(file_bytes):
    size = len(file_bytes)
    if size % 2 == 0:
        return "FORGED", 0.78, 10
    return "REAL", 0.64, 9

def save_result(filename, label, confidence, frames_analyzed):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO detections (filename, label, confidence, frames_analyzed, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, label, confidence, frames_analyzed, created_at))
    conn.commit()
    conn.close()
    return created_at

def load_history():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT filename, label, confidence, frames_analyzed, created_at
        FROM detections
        ORDER BY id DESC
        LIMIT 20
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

init_db()

st.title("Video Forgery Detection System")
st.write("Upload a video file and check whether it may be forged.")

uploaded_file = st.file_uploader("Choose a video", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file is not None:
    st.success(f"Selected file: {uploaded_file.name}")

    if st.button("Analyze Video"):
        with st.spinner("Analyzing video..."):
            file_bytes = uploaded_file.read()
            label, confidence, frames_analyzed = fake_model_prediction(file_bytes)
            created_at = save_result(uploaded_file.name, label, confidence, frames_analyzed)

            st.subheader("Prediction result")
            c1, c2, c3 = st.columns(3)
            c1.metric("Label", label)
            c2.metric("Confidence", f"{confidence:.2f}")
            c3.metric("Frames analyzed", frames_analyzed)

            st.json({
                "filename": uploaded_file.name,
                "label": label,
                "confidence": confidence,
                "frames_analyzed": frames_analyzed,
                "created_at": created_at
            })

st.subheader("Previous analyses")
if st.button("Load History"):
    rows = load_history()
    if rows:
        for row in rows:
            st.write({
                "filename": row[0],
                "label": row[1],
                "confidence": row[2],
                "frames_analyzed": row[3],
                "created_at": row[4]
            })
    else:
        st.info("No history found.")
    if total_frames > 0:
        step = max(1, total_frames // max_frames)
        for i in range(0, total_frames, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, _ = cap.read()
            if ret:
                frames_read += 1
            if frames_read >= max_frames:
                break

    cap.release()
    Path(temp_path).unlink(missing_ok=True)
    return frames_read

def fake_model_prediction(frames_analyzed):
    if frames_analyzed % 2 == 0:
        return "FORGED", 0.78
    return "REAL", 0.64

def save_result(filename, label, confidence, frames_analyzed):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO detections (filename, label, confidence, frames_analyzed, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, label, confidence, frames_analyzed, created_at))
    conn.commit()
    conn.close()
    return created_at

def load_history():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT filename, label, confidence, frames_analyzed, created_at
        FROM detections
        ORDER BY id DESC
        LIMIT 20
    """)
    rows = cur.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=["filename", "label", "confidence", "frames_analyzed", "created_at"])

init_db()

st.title("Video Forgery Detection System")
st.write("Upload a video file and check whether it may be forged.")

uploaded_file = st.file_uploader("Choose a video", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file is not None:
    st.success(f"Selected file: {uploaded_file.name}")

    if st.button("Analyze Video"):
        with st.spinner("Analyzing video..."):
            video_bytes = uploaded_file.read()
            frames_analyzed = extract_frames(video_bytes)
            label, confidence = fake_model_prediction(frames_analyzed)
            created_at = save_result(uploaded_file.name, label, confidence, frames_analyzed)

            st.subheader("Prediction result")
            c1, c2, c3 = st.columns(3)
            c1.metric("Label", label)
            c2.metric("Confidence", f"{confidence:.2f}")
            c3.metric("Frames analyzed", frames_analyzed)

            st.json({
                "filename": uploaded_file.name,
                "label": label,
                "confidence": confidence,
                "frames_analyzed": frames_analyzed,
                "created_at": created_at
            })

st.subheader("Previous analyses")
if st.button("Load History"):
    df = load_history()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No history found.")

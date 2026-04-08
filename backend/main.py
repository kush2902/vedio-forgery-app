from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import cv2
import shutil
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Video Forgery Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "detections.db"
UPLOAD_DIR = BASE_DIR.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

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

def extract_frames(video_path, max_frames=10):
    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_read = 0

    if total_frames <= 0:
        cap.release()
        return 0

    step = max(1, total_frames // max_frames)

    for i in range(0, total_frames, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, _ = cap.read()
        if ret:
            frames_read += 1
        if frames_read >= max_frames:
            break

    cap.release()
    return frames_read

def fake_model_prediction(frames_analyzed):
    if frames_analyzed % 2 == 0:
        return "FORGED", 0.78
    return "REAL", 0.64

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Video Forgery Detection API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    frames_analyzed = extract_frames(file_path)
    label, confidence = fake_model_prediction(frames_analyzed)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO detections (filename, label, confidence, frames_analyzed, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (file.filename, label, confidence, frames_analyzed, created_at))
    conn.commit()
    conn.close()

    return {
        "filename": file.filename,
        "label": label,
        "confidence": confidence,
        "frames_analyzed": frames_analyzed,
        "created_at": created_at
    }

@app.get("/history")
def history():
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

    result = []
    for row in rows:
        result.append({
            "filename": row[0],
            "label": row[1],
            "confidence": row[2],
            "frames_analyzed": row[3],
            "created_at": row[4]
        })
    return result

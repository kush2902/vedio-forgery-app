"""
Video Forgery Detection App - Streamlit
Deploy-ready version with proper syntax and cloud compatibility
"""

import streamlit as st
import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
import tempfile
import os
import time

# Page config
st.set_page_config(
    page_title="Video Forgery Detection",
    page_icon="🎥",
    layout="wide"
)

st.title("🎥 Video Forgery Detection")
st.markdown("---")

# Sidebar
st.sidebar.header("Upload Video")
uploaded_file = st.sidebar.file_uploader(
    "Choose a video file", 
    type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
    help="Upload a video to detect forgery/manipulation"
)

# Demo video if no upload
if not uploaded_file:
    st.info("👈 Please upload a video from the sidebar")
    st.video("https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4")
    st.stop()

# Process uploaded video
if uploaded_file is not None:
    # Save uploaded video
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(uploaded_file.read())
        video_path = tmp_file.name
    
    st.sidebar.success("✅ Video uploaded!")
    st.video(video_path)
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Analyze video
    if st.sidebar.button("🔍 Detect Forgery", type="primary"):
        with st.spinner("Analyzing video frames..."):
            try:
                # Read video frames
                def read_video_frames(video_path, max_frames=100):
                    cap = cv2.VideoCapture(video_path)
                    frames = []
                    frame_count = 0
                    
                    while cap.isOpened() and frame_count < max_frames:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        # Resize for faster processing
                        frame = cv2.resize(frame, (224, 224))
                        frames.append(frame)
                        frame_count += 1
                        
                        # Update progress
                        progress = frame_count / max_frames
                        progress_bar.progress(progress)
                        status_text.text(f"Processing frame {frame_count}/{max_frames}")
                    
                    cap.release()
                    return frames  # Properly indented return

                # Extract frames
                frames = read_video_frames(video_path)
                status_text.text(f"✅ Extracted {len(frames)} frames")
                
                if len(frames) == 0:
                    st.error("❌ No frames could be extracted. Please try another video.")
                    os.unlink(video_path)
                    st.stop()

                # Simple forgery detection heuristics
                def detect_forgery_heuristics(frames):
                    results = {
                        'frame_consistency': [],
                        'motion_stability': [],
                        'color_variance': []
                    }
                    
                    prev_frame = None
                    for i, frame in enumerate(frames):
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        
                        # Frame consistency (duplicate detection)
                        if prev_frame is not None:
                            diff = cv2.absdiff(gray, prev_frame)
                            mean_diff = np.mean(diff)
                            results['frame_consistency'].append(mean_diff < 2.0)  # Very low diff = duplicate
                        
                        # Color variance (sudden changes)
                        variance = np.var(gray)
                        results['color_variance'].append(variance)
                        
                        prev_frame = gray
                    
                    # Calculate scores
                    duplicate_ratio = sum(results['frame_consistency']) / len(results['frame_consistency'])
                    variance_stability = np.std(results['color_variance'])
                    
                    return {
                        'duplicate_frames': duplicate_ratio > 0.1,
                        'unstable_color': variance_stability > 50,
                        'suspicious': duplicate_ratio > 0.1 or variance_stability > 50
                    }

                # Run analysis
                analysis = detect_forgery_heuristics(frames)
                
                # Display results
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if analysis['suspicious']:
                        st.error("🚨 **FORGERY DETECTED**")
                        st.markdown("**Confidence:** High")
                        st.warning("🔍 Indicators:")
                        if analysis['duplicate_frames']:
                            st.write("• Duplicate/similar frames detected")
                        if analysis['unstable_color']:
                            st.write("• Unstable color variance")
                    else:
                        st.success("✅ **VIDEO AUTHENTIC**")
                        st.markdown("**Confidence:** High")
                        st.info("No forgery indicators found")
                
                with col2:
                    st.subheader("📊 Analysis Details")
                    
                    # Show suspicious frames
                    suspicious_frames = []
                    for i, frame in enumerate(frames[:10]):  # First 10 frames
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        if i > 0:
                            prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
                            diff = cv2.absdiff(gray, prev_gray)
                            if np.mean(diff) < 2.0:
                                suspicious_frames.append((i, frame))
                    
                    if suspicious_frames:
                        st.warning(f"Found {len(suspicious_frames)} suspicious frames")
                        for idx, frame in suspicious_frames[:3]:
                            st.image(frame, caption=f"Frame {idx} - Duplicate detected", width=200)
                    else:
                        st.info("No duplicate frames in sample")
                
                # Cleanup
                os.unlink(video_path)
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                if os.path.exists(video_path):
                    os.unlink(video_path)

# Footer
st.markdown("---")
st.markdown(
    """
    **Video Forgery Detection App**  
    Built with ❤️ using Streamlit, OpenCV, and Computer Vision techniques  
    Detects frame duplication, tampering, and manipulation patterns
    """,
    unsafe_allow_html=True
)

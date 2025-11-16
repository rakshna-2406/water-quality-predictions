#!/usr/bin/env python3
"""Simplified Streamlit app with lazy model loading"""
import os
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import streamlit as st
from pathlib import Path
import numpy as np
from PIL import Image

st.set_page_config(page_title="💧 Water Quality Prediction", layout="wide")

# CSS
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    h1 { color: white !important; text-align: center; }
    .uploadedFile { background: white; border-radius: 10px; padding: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("💧 Water Quality Prediction System")
st.markdown("<p style='text-align: center; color: white;'>Upload an image to check if water is safe to drink</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])

with col2:
    uploaded_file = st.file_uploader("Choose a water image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("🔍 Analyze Water Quality", use_container_width=True):
            with st.spinner("Analyzing..."):
                try:
                    # Import TensorFlow only when needed
                    from tensorflow.keras.models import load_model
                    from tensorflow.keras.preprocessing.image import img_to_array
                    
                    # Load model
                    model = load_model("best_model.h5", compile=False)
                    
                    # Preprocess
                    img = image.convert("RGB").resize((224, 224))
                    arr = img_to_array(img) / 255.0
                    arr = np.expand_dims(arr, axis=0)
                    
                    # Predict
                    prob = float(model.predict(arr, verbose=0)[0][0])
                    label = "Dirty" if prob >= 0.5 else "Clean"
                    confidence = prob * 100 if prob >= 0.5 else (1 - prob) * 100
                    
                    # Display result
                    if label == "Clean":
                        st.success(f"✅ **CLEAN WATER** - Safe to drink")
                        st.metric("Confidence", f"{confidence:.1f}%")
                        st.info("The model predicts this water is safe for consumption.")
                    else:
                        st.error(f"⚠️ **DIRTY WATER** - Not safe to drink")
                        st.metric("Confidence", f"{confidence:.1f}%")
                        st.warning("The model predicts this water is NOT safe for consumption.")
                    
                    st.caption(f"Raw prediction score: {prob:.4f} (>0.5 = Dirty, <0.5 = Clean)")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white;'>
    <p><strong>Model:</strong> MobileNetV2 | <strong>Accuracy:</strong> 57.14%</p>
    <p>Trained on 38 images | Tested on 14 images</p>
</div>
""", unsafe_allow_html=True)

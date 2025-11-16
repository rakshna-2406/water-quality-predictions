"""
Water Quality Prediction App
A simple Streamlit application for predicting water quality from images
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import streamlit as st
import numpy as np
from PIL import Image
from pathlib import Path

# Pre-load TensorFlow and model at startup (before any threading)
@st.cache_resource
def load_prediction_model():
    """Load model once and cache it"""
    from tensorflow.keras.models import load_model
    model_path = Path("best_model.h5")
    if model_path.exists():
        return load_model(str(model_path), compile=False)
    return None

# Page config
st.set_page_config(
    page_title="Water Quality Prediction",
    page_icon="💧",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    h1 {
        color: white !important;
        text-align: center;
        padding: 20px;
    }
    .subtitle {
        color: white;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    .result-box {
        background: white;
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("# 💧 Water Quality Prediction")
st.markdown('<p class="subtitle">Upload an image to check if water is safe to drink</p>', unsafe_allow_html=True)

# Load model at startup
try:
    model = load_prediction_model()
    if model is None:
        st.error("❌ Model file not found! Please train the model first.")
        st.code("python3 train_model.py --epochs 10")
        st.stop()
except Exception as e:
    st.error(f"❌ Error loading model: {str(e)}")
    st.stop()

# File uploader
uploaded_file = st.file_uploader(
    "Choose a water image",
    type=["jpg", "jpeg", "png"],
    help="Upload an image of water to analyze"
)

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Analyze button
    if st.button("🔍 Analyze Water Quality", type="primary", use_container_width=True):
        with st.spinner("Analyzing image..."):
            try:
                from tensorflow.keras.preprocessing.image import img_to_array
                
                # Preprocess image
                img_resized = image.convert("RGB").resize((224, 224))
                img_array = img_to_array(img_resized) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                
                # Make prediction using pre-loaded model
                prediction = model.predict(img_array, verbose=0)
                probability = float(prediction[0][0])
                
                # Determine label and confidence
                if probability >= 0.5:
                    label = "Dirty"
                    confidence = probability * 100
                    is_safe = False
                else:
                    label = "Clean"
                    confidence = (1 - probability) * 100
                    is_safe = True
                
                # Display results
                st.markdown("---")
                
                if is_safe:
                    st.success("### ✅ CLEAN WATER")
                    st.markdown("**Status:** Safe to drink")
                    st.balloons()
                else:
                    st.error("### ⚠️ DIRTY WATER")
                    st.markdown("**Status:** NOT safe to drink")
                
                # Metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Prediction", label)
                with col2:
                    st.metric("Confidence", f"{confidence:.1f}%")
                
                # Additional info
                with st.expander("📊 Technical Details"):
                    st.write(f"**Raw Score:** {probability:.4f}")
                    st.write(f"**Threshold:** 0.5")
                    st.write(f"**Model:** MobileNetV2")
                    st.write(f"**Input Size:** 224x224")
                    
                    if probability >= 0.5:
                        st.write(f"**Interpretation:** Score > 0.5 indicates dirty water")
                    else:
                        st.write(f"**Interpretation:** Score < 0.5 indicates clean water")
                
            except Exception as e:
                st.error(f"❌ Error during prediction: {str(e)}")
                st.exception(e)

else:
    # Instructions when no file is uploaded
    st.info("👆 Please upload an image to get started")
    
    # Show example
    st.markdown("---")
    st.markdown("### 📝 How it works:")
    st.markdown("""
    1. **Upload** an image of water
    2. Click **Analyze** button
    3. Get instant prediction: Clean or Dirty
    4. View confidence score
    """)
    
    # Model info
    st.markdown("---")
    st.markdown("### 🤖 Model Information:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Model", "MobileNetV2")
    with col2:
        st.metric("Accuracy", "57.14%")
    with col3:
        st.metric("Test Images", "14")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: white; opacity: 0.8;">Built with Streamlit & TensorFlow</p>',
    unsafe_allow_html=True
)

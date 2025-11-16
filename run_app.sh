#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Set environment variables to fix TensorFlow threading issues on macOS
export OMP_NUM_THREADS=1
export KMP_DUPLICATE_LIB_OK=TRUE
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Run Streamlit
echo "Starting Water Quality Prediction System..."
echo "The app will be available at: http://localhost:8501"
echo ""
streamlit run streamlit_app.py

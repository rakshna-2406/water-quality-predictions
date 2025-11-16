#!/usr/bin/env python3
"""
Flask API Server for Water Quality Prediction
Deploy this to Render, Railway, or Google Cloud Run
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['OMP_NUM_THREADS'] = '1'

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

# Enable CORS for Firebase domain
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://water-quailty-prediction-raks.web.app",
            "https://water-quailty-prediction-raks.firebaseapp.com",
            "http://localhost:5000",
            "http://localhost:5555"
        ]
    }
})

# Load model at startup
print("Loading TensorFlow model...")
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

model = load_model("best_model.h5", compile=False)
print("Model loaded successfully!")

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'Water Quality Prediction API',
        'version': '1.0',
        'model': 'MobileNetV2',
        'endpoints': {
            '/': 'API info',
            '/health': 'Health check',
            '/predict': 'POST - Predict water quality from image'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read and process image
        image_bytes = file.read()
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB').resize((224, 224))
        
        # Convert to array and normalize
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Make prediction
        prediction = model.predict(img_array, verbose=0)
        probability = float(prediction[0][0])
        
        # Determine label and confidence
        if probability >= 0.5:
            label = "Dirty"
            confidence = probability * 100
            message = "✗ NOT safe to drink"
        else:
            label = "Clean"
            confidence = (1 - probability) * 100
            message = "✓ Safe to drink"
        
        return jsonify({
            'label': label,
            'confidence': confidence,
            'probability': probability,
            'message': message,
            'success': True
        })
    
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=False)

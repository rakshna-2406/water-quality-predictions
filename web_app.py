#!/usr/bin/env python3
"""
Simple Flask Web App for Water Quality Prediction
No threading issues - works on macOS
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['OMP_NUM_THREADS'] = '1'

from flask import Flask, render_template_string, request, jsonify
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import io
import base64

app = Flask(__name__)

# Load model once at startup
print("Loading model...")
model = load_model("best_model.h5", compile=False)
print("Model loaded successfully!")

IMG_SIZE = (224, 224)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>💧 Water Quality Prediction</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            background: #f8f9ff;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-area:hover {
            background: #eef1ff;
            border-color: #764ba2;
        }
        .upload-area input {
            display: none;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 18px;
            cursor: pointer;
            width: 100%;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .result {
            margin-top: 30px;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            display: none;
        }
        .result.clean {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .result.dirty {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .result h2 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        .result .confidence {
            font-size: 1.5em;
            margin: 10px 0;
        }
        .result .message {
            font-size: 1.2em;
            margin-top: 15px;
        }
        .preview {
            max-width: 100%;
            max-height: 300px;
            margin: 20px auto;
            display: none;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
            color: #667eea;
            font-size: 18px;
        }
        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 30px;
        }
        .stat-card {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .stat-card p {
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💧 Water Quality Prediction</h1>
        <p class="subtitle">Upload an image to check if water is safe to drink</p>
        
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <h3>📸 Click to Upload Image</h3>
            <p>Supports: JPG, JPEG, PNG</p>
            <input type="file" id="fileInput" accept="image/*" onchange="handleFileSelect(event)">
        </div>
        
        <img id="preview" class="preview">
        
        <button class="btn" id="predictBtn" onclick="predictImage()" disabled>
            Analyze Water Quality
        </button>
        
        <div class="loading" id="loading">
            🔄 Analyzing image...
        </div>
        
        <div class="result" id="result">
            <h2 id="resultLabel"></h2>
            <div class="confidence" id="confidence"></div>
            <div class="message" id="message"></div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Model</h3>
                <p>MobileNetV2</p>
            </div>
            <div class="stat-card">
                <h3>Accuracy</h3>
                <p>57.14%</p>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                selectedFile = file;
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('preview');
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    document.getElementById('predictBtn').disabled = false;
                    document.getElementById('result').style.display = 'none';
                };
                reader.readAsDataURL(file);
            }
        }

        async function predictImage() {
            if (!selectedFile) return;

            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.getElementById('predictBtn').disabled = true;

            const formData = new FormData();
            formData.append('image', selectedFile);

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                document.getElementById('loading').style.display = 'none';
                
                const result = document.getElementById('result');
                result.className = 'result ' + data.label.toLowerCase();
                result.style.display = 'block';
                
                document.getElementById('resultLabel').textContent = 
                    data.label === 'Clean' ? '✓ Clean Water' : '✗ Dirty Water';
                document.getElementById('confidence').textContent = 
                    'Confidence: ' + data.confidence.toFixed(1) + '%';
                document.getElementById('message').textContent = data.message;
                
                document.getElementById('predictBtn').disabled = false;
            } catch (error) {
                alert('Error: ' + error.message);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('predictBtn').disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    
    # Read and process image
    img = Image.open(file.stream).convert('RGB').resize(IMG_SIZE)
    arr = img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    
    # Predict
    prob = float(model.predict(arr, verbose=0)[0][0])
    label = "Dirty" if prob >= 0.5 else "Clean"
    confidence = prob * 100 if prob >= 0.5 else (1 - prob) * 100
    
    if label == "Clean":
        message = "✓ Water appears SAFE to drink (according to model)"
    else:
        message = "✗ Water appears NOT SAFE to drink (according to model)"
    
    return jsonify({
        'label': label,
        'confidence': confidence,
        'probability': prob,
        'message': message
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("💧 WATER QUALITY PREDICTION SYSTEM")
    print("="*70)
    print("\n🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("\n✓ Upload an image to check water quality")
    print("✓ Get instant predictions: Clean or Dirty")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

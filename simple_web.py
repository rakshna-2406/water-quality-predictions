#!/usr/bin/env python3
"""Simple web server without Streamlit"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['OMP_NUM_THREADS'] = '1'

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import base64
import io
from PIL import Image
import numpy as np

# Load model at startup
print("Loading model...")
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

model = load_model("best_model.h5", compile=False)
print("Model loaded successfully!")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Water Quality Prediction</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
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
            cursor: pointer;
            transition: all 0.3s;
            background: #f8f9ff;
        }
        .upload-area:hover {
            background: #eef1ff;
            border-color: #764ba2;
        }
        .upload-area.dragover {
            background: #e0e7ff;
            border-color: #667eea;
        }
        input[type="file"] { display: none; }
        #preview {
            max-width: 100%;
            max-height: 300px;
            margin: 20px auto;
            display: none;
            border-radius: 10px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 18px;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        button:disabled {
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
        .result h2 { margin-bottom: 15px; }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
            color: #667eea;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💧 Water Quality Prediction</h1>
        <p class="subtitle">Upload an image to check if water is safe to drink</p>
        
        <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
            <h3>📸 Click or Drag to Upload Image</h3>
            <p>Supports: JPG, JPEG, PNG</p>
            <input type="file" id="fileInput" accept="image/*">
        </div>
        
        <img id="preview">
        
        <button id="analyzeBtn" onclick="analyzeImage()" disabled>
            🔍 Analyze Water Quality
        </button>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Analyzing image...</p>
        </div>
        
        <div class="result" id="result">
            <h2 id="resultLabel"></h2>
            <p id="confidence" style="font-size: 1.5em; margin: 10px 0;"></p>
            <p id="message" style="font-size: 1.2em;"></p>
        </div>
    </div>

    <script>
        let selectedFile = null;
        const fileInput = document.getElementById('fileInput');
        const preview = document.getElementById('preview');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const uploadArea = document.getElementById('uploadArea');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');

        fileInput.addEventListener('change', handleFileSelect);
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect();
            }
        });

        function handleFileSelect() {
            const file = fileInput.files[0];
            if (file) {
                selectedFile = file;
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    analyzeBtn.disabled = false;
                    result.style.display = 'none';
                };
                reader.readAsDataURL(file);
            }
        }

        async function analyzeImage() {
            if (!selectedFile) return;

            loading.style.display = 'block';
            result.style.display = 'none';
            analyzeBtn.disabled = true;

            const formData = new FormData();
            formData.append('image', selectedFile);

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                loading.style.display = 'none';
                
                result.className = 'result ' + data.label.toLowerCase();
                result.style.display = 'block';
                
                document.getElementById('resultLabel').textContent = 
                    data.label === 'Clean' ? '✅ CLEAN WATER' : '⚠️ DIRTY WATER';
                document.getElementById('confidence').textContent = 
                    'Confidence: ' + data.confidence.toFixed(1) + '%';
                document.getElementById('message').textContent = data.message;
                
                analyzeBtn.disabled = false;
            } catch (error) {
                loading.style.display = 'none';
                alert('Error: ' + error.message);
                analyzeBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML.encode())
    
    def do_POST(self):
        if self.path == '/predict':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse multipart form data (simple version)
            boundary = self.headers['Content-Type'].split('boundary=')[1]
            parts = post_data.split(('--' + boundary).encode())
            
            image_data = None
            for part in parts:
                if b'Content-Type: image' in part:
                    image_data = part.split(b'\r\n\r\n')[1].rsplit(b'\r\n', 1)[0]
                    break
            
            if image_data:
                try:
                    # Process image
                    img = Image.open(io.BytesIO(image_data)).convert('RGB').resize((224, 224))
                    arr = img_to_array(img) / 255.0
                    arr = np.expand_dims(arr, axis=0)
                    
                    # Predict
                    prob = float(model.predict(arr, verbose=0)[0][0])
                    label = "Dirty" if prob >= 0.5 else "Clean"
                    confidence = prob * 100 if prob >= 0.5 else (1 - prob) * 100
                    
                    message = "✓ Safe to drink" if label == "Clean" else "✗ NOT safe to drink"
                    
                    response = {
                        'label': label,
                        'confidence': confidence,
                        'probability': prob,
                        'message': message
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode())
            else:
                self.send_response(400)
                self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress log messages

if __name__ == '__main__':
    PORT = 5555
    server = HTTPServer(('0.0.0.0', PORT), RequestHandler)
    print("\n" + "="*70)
    print("💧 WATER QUALITY PREDICTION SYSTEM")
    print("="*70)
    print(f"\n🌐 Server running at: http://localhost:{PORT}")
    print(f"📱 Open your browser and go to: http://localhost:{PORT}")
    print("\n✓ Upload an image to check water quality")
    print("✓ Get instant predictions: Clean or Dirty")
    print("\nPress Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        server.shutdown()

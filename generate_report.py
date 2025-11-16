#!/usr/bin/env python3
"""Generate HTML report with all results"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
from pathlib import Path
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array
import sklearn.metrics as skm
import base64
from io import BytesIO

print("Generating complete HTML report...")

# Load model
model = load_model("best_model.h5", compile=False)

# Evaluate on test set
IMG_SIZE = (224, 224)
data_dir = "data/water images"
test_dir = Path(data_dir) / "test"

test_datagen = ImageDataGenerator(rescale=1./255)
test_flow = test_datagen.flow_from_directory(
    str(test_dir),
    target_size=IMG_SIZE,
    batch_size=16,
    class_mode='binary',
    shuffle=False
)

preds = model.predict(test_flow, verbose=0).ravel()
y_pred = (preds >= 0.5).astype(int)
y_true = test_flow.classes

acc = (y_pred == y_true).mean()
cm = skm.confusion_matrix(y_true, y_pred)
report = skm.classification_report(y_true, y_pred, 
                                   target_names=['Clean', 'Dirty'],
                                   digits=3,
                                   output_dict=True)

# Get sample predictions with images
clean_images = list(Path(test_dir / "Clean-samples").glob("*.jpg"))[:3]
dirty_images = list(Path(test_dir / "Dirty-samples").glob("*.jpg"))[:3]

def img_to_base64(img_path):
    img = Image.open(img_path)
    img.thumbnail((300, 300))
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def predict_image(img_path):
    img = Image.open(img_path).convert("RGB").resize(IMG_SIZE)
    arr = img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    prob = float(model.predict(arr, verbose=0)[0][0])
    label = "Dirty" if prob >= 0.5 else "Clean"
    confidence = prob * 100 if prob >= 0.5 else (1 - prob) * 100
    return label, confidence, prob

# Generate HTML
html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Water Quality Prediction - Complete Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        h2 {{
            color: #764ba2;
            margin: 30px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 1.2em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .stat-card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        .confusion-matrix {{
            margin: 20px 0;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 15px;
            text-align: center;
            border: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background: #f8f9ff;
        }}
        .predictions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .prediction-card {{
            border: 2px solid #ddd;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .prediction-card img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
        }}
        .prediction-info {{
            padding: 20px;
        }}
        .prediction-info.clean {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }}
        .prediction-info.dirty {{
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }}
        .prediction-info h4 {{
            margin-bottom: 10px;
            font-size: 1.3em;
        }}
        .prediction-info p {{
            margin: 5px 0;
        }}
        .correct {{ color: #38ef7d; font-weight: bold; }}
        .incorrect {{ color: #f45c43; font-weight: bold; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>💧 Water Quality Prediction System</h1>
        <p class="subtitle">Complete Analysis Report - Generated {Path('best_model.h5').stat().st_mtime}</p>
        
        <h2>📊 Overall Performance</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Overall Accuracy</h3>
                <div class="value">{acc*100:.1f}%</div>
            </div>
            <div class="stat-card">
                <h3>Test Images</h3>
                <div class="value">{test_flow.samples}</div>
            </div>
            <div class="stat-card">
                <h3>Correct Predictions</h3>
                <div class="value">{(y_pred == y_true).sum()}</div>
            </div>
            <div class="stat-card">
                <h3>Model Type</h3>
                <div class="value" style="font-size: 1.5em;">MobileNetV2</div>
            </div>
        </div>
        
        <h2>📋 Confusion Matrix</h2>
        <div class="confusion-matrix">
            <table>
                <tr>
                    <th></th>
                    <th>Predicted Clean</th>
                    <th>Predicted Dirty</th>
                </tr>
                <tr>
                    <th>Actual Clean</th>
                    <td>{cm[0][0]}</td>
                    <td>{cm[0][1]}</td>
                </tr>
                <tr>
                    <th>Actual Dirty</th>
                    <td>{cm[1][0]}</td>
                    <td>{cm[1][1]}</td>
                </tr>
            </table>
        </div>
        
        <h2>📈 Detailed Metrics</h2>
        <table>
            <tr>
                <th>Class</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
                <th>Support</th>
            </tr>
            <tr>
                <td><strong>Clean Water</strong></td>
                <td>{report['Clean']['precision']*100:.1f}%</td>
                <td>{report['Clean']['recall']*100:.1f}%</td>
                <td>{report['Clean']['f1-score']*100:.1f}%</td>
                <td>{int(report['Clean']['support'])}</td>
            </tr>
            <tr>
                <td><strong>Dirty Water</strong></td>
                <td>{report['Dirty']['precision']*100:.1f}%</td>
                <td>{report['Dirty']['recall']*100:.1f}%</td>
                <td>{report['Dirty']['f1-score']*100:.1f}%</td>
                <td>{int(report['Dirty']['support'])}</td>
            </tr>
        </table>
        
        <h2>🔍 Sample Predictions - Clean Water</h2>
        <div class="predictions-grid">
"""

for img_path in clean_images:
    label, confidence, prob = predict_image(img_path)
    img_b64 = img_to_base64(img_path)
    correct = label == "Clean"
    status = "✓ CORRECT" if correct else "✗ INCORRECT"
    html += f"""
            <div class="prediction-card">
                <img src="data:image/jpeg;base64,{img_b64}" alt="{img_path.name}">
                <div class="prediction-info {label.lower()}">
                    <h4>{status}</h4>
                    <p><strong>Actual:</strong> Clean</p>
                    <p><strong>Predicted:</strong> {label}</p>
                    <p><strong>Confidence:</strong> {confidence:.1f}%</p>
                    <p><strong>File:</strong> {img_path.name}</p>
                </div>
            </div>
"""

html += """
        </div>
        
        <h2>🔍 Sample Predictions - Dirty Water</h2>
        <div class="predictions-grid">
"""

for img_path in dirty_images:
    label, confidence, prob = predict_image(img_path)
    img_b64 = img_to_base64(img_path)
    correct = label == "Dirty"
    status = "✓ CORRECT" if correct else "✗ INCORRECT"
    html += f"""
            <div class="prediction-card">
                <img src="data:image/jpeg;base64,{img_b64}" alt="{img_path.name}">
                <div class="prediction-info {label.lower()}">
                    <h4>{status}</h4>
                    <p><strong>Actual:</strong> Dirty</p>
                    <p><strong>Predicted:</strong> {label}</p>
                    <p><strong>Confidence:</strong> {confidence:.1f}%</p>
                    <p><strong>File:</strong> {img_path.name}</p>
                </div>
            </div>
"""

html += f"""
        </div>
        
        <div class="footer">
            <p><strong>Water Quality Prediction System</strong></p>
            <p>Model: MobileNetV2 | Accuracy: {acc*100:.1f}% | Test Images: {test_flow.samples}</p>
            <p>Generated on: {Path('best_model.h5').stat().st_mtime}</p>
        </div>
    </div>
</body>
</html>
"""

# Save HTML file
with open("water_quality_report.html", "w") as f:
    f.write(html)

print("\n" + "="*70)
print("✅ REPORT GENERATED SUCCESSFULLY!")
print("="*70)
print(f"\n📄 File saved: water_quality_report.html")
print(f"\n🌐 Open this file in your browser to see the complete results!")
print(f"\nTo open it:")
print(f"  • Double-click: water_quality_report.html")
print(f"  • Or run: open water_quality_report.html")
print("\n" + "="*70)

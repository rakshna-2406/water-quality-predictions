#!/usr/bin/env python3
"""
Simple script to predict water quality from an image
Usage: python3 predict_image.py <image_path>
"""
import sys
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

IMG_SIZE = (224, 224)

def predict_image(model_path, image_path):
    # Load model
    print(f"Loading model: {model_path}")
    model = load_model(model_path)
    
    # Load and preprocess image
    print(f"Loading image: {image_path}")
    img = Image.open(image_path).convert("RGB").resize(IMG_SIZE)
    arr = img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    
    # Predict
    prob = float(model.predict(arr, verbose=0)[0][0])
    label = "Dirty" if prob >= 0.5 else "Clean"
    confidence = prob * 100 if prob >= 0.5 else (1 - prob) * 100
    
    # Display results
    print("\n" + "="*50)
    print("WATER QUALITY PREDICTION")
    print("="*50)
    print(f"Prediction: {label}")
    print(f"Confidence: {confidence:.2f}%")
    print(f"Raw score: {prob:.4f} (>0.5 = Dirty, <0.5 = Clean)")
    
    if label == "Clean":
        print("\n✓ Water appears SAFE to drink (according to model)")
    else:
        print("\n✗ Water appears NOT SAFE to drink (according to model)")
    print("="*50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 predict_image.py <image_path>")
        print("Example: python3 predict_image.py test_image.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    model_path = "best_model.h5"
    
    predict_image(model_path, image_path)

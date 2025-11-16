#!/usr/bin/env python3
"""Evaluate model on test set"""
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pathlib import Path
import sklearn.metrics as skm

IMG_SIZE = (224, 224)
data_dir = "data/water images"
test_dir = Path(data_dir) / "test"

# Load model
print("Loading model...")
model = load_model("best_model.h5")

# Prepare test data
test_datagen = ImageDataGenerator(rescale=1./255)
test_flow = test_datagen.flow_from_directory(
    str(test_dir),
    target_size=IMG_SIZE,
    batch_size=16,
    class_mode='binary',
    shuffle=False
)

print(f"\nFound {test_flow.samples} test images")
print(f"Classes: {test_flow.class_indices}")

# Predict
print("\nMaking predictions...")
preds = model.predict(test_flow, verbose=1).ravel()
y_pred = (preds >= 0.5).astype(int)
y_true = test_flow.classes

# Calculate metrics
acc = (y_pred == y_true).mean()
cm = skm.confusion_matrix(y_true, y_pred)

print("\n" + "="*60)
print("MODEL EVALUATION RESULTS")
print("="*60)
print(f"Overall Accuracy: {acc*100:.2f}%")
print(f"\nConfusion Matrix:")
print(f"                Predicted Clean  Predicted Dirty")
print(f"Actual Clean         {cm[0][0]:3d}              {cm[0][1]:3d}")
print(f"Actual Dirty         {cm[1][0]:3d}              {cm[1][1]:3d}")

# Per-class metrics
report = skm.classification_report(y_true, y_pred, 
                                   target_names=['Clean', 'Dirty'],
                                   digits=3)
print(f"\nDetailed Classification Report:")
print(report)
print("="*60)

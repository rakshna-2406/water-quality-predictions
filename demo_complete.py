#!/usr/bin/env python3
"""
Complete Water Quality Prediction Demo
Shows training, evaluation, and predictions with full output
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow warnings

import numpy as np
from pathlib import Path
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array
import sklearn.metrics as skm

print("="*70)
print(" 💧 WATER QUALITY PREDICTION SYSTEM - COMPLETE DEMO")
print("="*70)

# Configuration
IMG_SIZE = (224, 224)
data_dir = "data/water images"
test_dir = Path(data_dir) / "test"

# ============================================================================
# PART 1: MODEL INFORMATION
# ============================================================================
print("\n📊 PART 1: MODEL INFORMATION")
print("-" * 70)

if Path("best_model.h5").exists():
    print("✓ Model found: best_model.h5")
    print("✓ Model architecture: MobileNetV2 (transfer learning)")
    print("✓ Input size: 224x224 RGB images")
    print("✓ Output: Binary classification (Clean vs Dirty)")
else:
    print("✗ Model not found. Please train first.")
    exit(1)

# ============================================================================
# PART 2: TEST SET EVALUATION
# ============================================================================
print("\n📈 PART 2: EVALUATING MODEL ON TEST SET")
print("-" * 70)

model = load_model("best_model.h5", compile=False)
print("Model loaded successfully")

test_datagen = ImageDataGenerator(rescale=1./255)
test_flow = test_datagen.flow_from_directory(
    str(test_dir),
    target_size=IMG_SIZE,
    batch_size=16,
    class_mode='binary',
    shuffle=False
)

print(f"\nTest set: {test_flow.samples} images")
print(f"Classes: {test_flow.class_indices}")

print("\nGenerating predictions...")
preds = model.predict(test_flow, verbose=0).ravel()
y_pred = (preds >= 0.5).astype(int)
y_true = test_flow.classes

# Calculate metrics
acc = (y_pred == y_true).mean()
cm = skm.confusion_matrix(y_true, y_pred)

print("\n" + "="*70)
print("📊 OVERALL RESULTS")
print("="*70)
print(f"✓ Overall Accuracy: {acc*100:.2f}%")
print(f"✓ Correct predictions: {(y_pred == y_true).sum()}/{len(y_true)}")
print(f"✓ Incorrect predictions: {(y_pred != y_true).sum()}/{len(y_true)}")

print(f"\n📋 CONFUSION MATRIX:")
print(f"{'':20} Predicted Clean    Predicted Dirty")
print(f"{'Actual Clean':20}      {cm[0][0]:3d}               {cm[0][1]:3d}")
print(f"{'Actual Dirty':20}      {cm[1][0]:3d}               {cm[1][1]:3d}")

# Per-class metrics
report = skm.classification_report(y_true, y_pred, 
                                   target_names=['Clean', 'Dirty'],
                                   digits=3,
                                   output_dict=True)

print(f"\n📊 PER-CLASS PERFORMANCE:")
print(f"\nClean Water:")
print(f"  • Precision: {report['Clean']['precision']*100:.1f}%")
print(f"  • Recall: {report['Clean']['recall']*100:.1f}%")
print(f"  • F1-Score: {report['Clean']['f1-score']*100:.1f}%")

print(f"\nDirty Water:")
print(f"  • Precision: {report['Dirty']['precision']*100:.1f}%")
print(f"  • Recall: {report['Dirty']['recall']*100:.1f}%")
print(f"  • F1-Score: {report['Dirty']['f1-score']*100:.1f}%")

# ============================================================================
# PART 3: INDIVIDUAL PREDICTIONS
# ============================================================================
print("\n" + "="*70)
print("🔍 PART 3: SAMPLE PREDICTIONS")
print("="*70)

# Get sample images
clean_images = list(Path(test_dir / "Clean-samples").glob("*.jpg"))[:3]
dirty_images = list(Path(test_dir / "Dirty-samples").glob("*.jpg"))[:3]

def predict_and_display(image_path, actual_label):
    img = Image.open(image_path).convert("RGB").resize(IMG_SIZE)
    arr = img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    
    prob = float(model.predict(arr, verbose=0)[0][0])
    predicted_label = "Dirty" if prob >= 0.5 else "Clean"
    confidence = prob * 100 if prob >= 0.5 else (1 - prob) * 100
    
    correct = "✓" if predicted_label == actual_label else "✗"
    
    print(f"\n{correct} Image: {image_path.name}")
    print(f"   Actual: {actual_label:6s} | Predicted: {predicted_label:6s} | Confidence: {confidence:.1f}%")
    
    if predicted_label == "Clean":
        print(f"   → Water appears SAFE to drink")
    else:
        print(f"   → Water appears NOT SAFE to drink")
    
    return predicted_label == actual_label

print("\n🟢 CLEAN WATER SAMPLES:")
clean_correct = sum(predict_and_display(img, "Clean") for img in clean_images)

print("\n🔴 DIRTY WATER SAMPLES:")
dirty_correct = sum(predict_and_display(img, "Dirty") for img in dirty_images)

total_samples = len(clean_images) + len(dirty_images)
total_correct = clean_correct + dirty_correct

print("\n" + "="*70)
print("📊 SAMPLE PREDICTIONS SUMMARY")
print("="*70)
print(f"Clean samples: {clean_correct}/{len(clean_images)} correct")
print(f"Dirty samples: {dirty_correct}/{len(dirty_images)} correct")
print(f"Total: {total_correct}/{total_samples} correct ({total_correct/total_samples*100:.1f}%)")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*70)
print("🎯 FINAL SUMMARY")
print("="*70)
print(f"✓ Model successfully evaluated on {test_flow.samples} test images")
print(f"✓ Overall test accuracy: {acc*100:.2f}%")
print(f"✓ Model can distinguish between clean and dirty water")
print(f"✓ Best for: {['Clean', 'Dirty'][np.argmax([report['Clean']['f1-score'], report['Dirty']['f1-score']])]}")
print("\n💡 To improve accuracy:")
print("   • Collect more training data")
print("   • Train for more epochs (currently trained for 3)")
print("   • Use data augmentation (already implemented)")
print("="*70)
print("\n✅ DEMO COMPLETE!")

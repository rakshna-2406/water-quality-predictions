# streamlit_app.py
# Glassmorphism-styled Streamlit App for Water Quality Prediction (Clean vs Dirty)
import os
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import streamlit as st
from pathlib import Path
import zipfile, tempfile, json
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import sklearn.metrics as skm

st.set_page_config(page_title="Water Quality Prediction System", layout="wide")

# -------------------------
# Glassmorphism CSS
# -------------------------
st.markdown(
    """
    <style>
    :root{
      --bg:#0f1724;
      --card: rgba(255,255,255,0.06);
      --glass: rgba(255,255,255,0.06);
      --accent: rgba(99,102,241,0.9);
      --muted: rgba(255,255,255,0.65);
    }
    html, body, [class*="stApp"] {
      background: linear-gradient(180deg, #071126 0%, #081827 100%);
      color: #e6eef8;
    }
    .glass {
      background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 8px 30px rgba(2,6,23,0.6);
      backdrop-filter: blur(8px) saturate(120%);
    }
    .header {
      font-size: 26px;
      font-weight: 700;
      margin-bottom: 6px;
      color: white;
    }
    .muted { color: var(--muted); font-size: 14px; }
    .btn {
      background: linear-gradient(90deg, rgba(99,102,241,1), rgba(129,140,248,1));
      color: white;
      border-radius: 8px;
      padding: 8px 12px;
    }
    .small { font-size: 13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Constants & Helpers
# -------------------------
IMG_SIZE = (224, 224)
DEFAULT_DATA_PATH = "data/water images"

def build_model(img_shape=(224,224,3), lr=1e-4, base_trainable=False):
    base = MobileNetV2(weights='imagenet', include_top=False, input_shape=img_shape)
    base.trainable = base_trainable
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.3)(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.2)(x)
    out = Dense(1, activation='sigmoid')(x)
    model = Model(inputs=base.input, outputs=out)
    model.compile(optimizer=Adam(lr), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def prepare_generators(data_dir, img_size=(224,224), batch_size=16, val_split=0.2):
    train_dir = Path(data_dir) / "train"
    test_dir = Path(data_dir) / "test"
    if not train_dir.exists():
        raise FileNotFoundError("train folder not found: " + str(train_dir))
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        brightness_range=(0.8,1.2),
        shear_range=0.05,
        zoom_range=0.1,
        validation_split=val_split
    )
    test_datagen = ImageDataGenerator(rescale=1./255)
    train_flow = train_datagen.flow_from_directory(str(train_dir), target_size=img_size, batch_size=batch_size, class_mode='binary', subset='training', shuffle=True)
    val_flow = train_datagen.flow_from_directory(str(train_dir), target_size=img_size, batch_size=batch_size, class_mode='binary', subset='validation', shuffle=True)
    test_flow = None
    if test_dir.exists():
        test_flow = test_datagen.flow_from_directory(str(test_dir), target_size=img_size, batch_size=batch_size, class_mode='binary', shuffle=False)
    return train_flow, val_flow, test_flow

def train_and_save(data_dir, epochs=8, batch_size=16):
    train_flow, val_flow, test_flow = prepare_generators(data_dir, IMG_SIZE, batch_size)
    model = build_model(img_shape=(IMG_SIZE[0],IMG_SIZE[1],3), lr=1e-4, base_trainable=False)
    callbacks = [
        ModelCheckpoint("best_model.h5", monitor='val_accuracy', save_best_only=True, verbose=1),
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
    ]
    steps = max(1, train_flow.samples // train_flow.batch_size)
    val_steps = max(1, val_flow.samples // val_flow.batch_size)
    history = model.fit(train_flow, epochs=epochs, steps_per_epoch=steps, validation_data=val_flow, validation_steps=val_steps, callbacks=callbacks, verbose=1)
    model.save("final_model.h5")
    with open("training_history.json","w") as f:
        json.dump({k:[float(x) for x in v] for k,v in history.history.items()}, f)
    return model, history, test_flow

def evaluate_model_on_test(model_path, data_dir):
    model = load_model(model_path)
    _, _, test_flow = prepare_generators(data_dir)
    if test_flow is None:
        raise FileNotFoundError("No test folder found.")
    preds = model.predict(test_flow, verbose=1).ravel()
    y_pred = (preds >= 0.5).astype(int)
    y_true = test_flow.classes
    acc = float((y_pred == y_true).mean())
    report = skm.classification_report(y_true, y_pred, target_names=list(test_flow.class_indices.keys()), output_dict=True)
    cm = skm.confusion_matrix(y_true, y_pred)
    return acc, report, cm

def predict_image_with_model(model_path, pil_image):
    model = load_model(model_path)
    img = pil_image.convert("RGB").resize(IMG_SIZE)
    arr = img_to_array(img)/255.0
    arr = np.expand_dims(arr, axis=0)
    prob = float(model.predict(arr)[0][0])
    label = "Dirty" if prob >= 0.5 else "Clean"
    drinkable = "Not safe to drink" if label=="Dirty" else "Safe to drink"
    return label, prob, drinkable, img

# -------------------------
# UI Layout (glass cards)
# -------------------------
st.markdown("<div class='glass header'>💧 Water Quality Prediction System</div>", unsafe_allow_html=True)
st.markdown("<div class='muted small'>Upload dataset → Train model → Upload image → Predict (Clean vs Dirty)</div>", unsafe_allow_html=True)
st.markdown("<br/>")

left, right = st.columns([1,2])

with left:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("Dataset & Training")
    st.write("Dataset structure: `root/train/<class_folder>` and optional `root/test/<class_folder>`")
    uploaded_zip = st.file_uploader("Upload dataset zip (optional)", type=["zip"])
    data_dir_input = st.text_input("Or enter dataset folder path", value=DEFAULT_DATA_PATH)
    epochs = st.number_input("Epochs", min_value=1, max_value=50, value=6)
    batch_size = st.number_input("Batch size", min_value=4, max_value=64, value=16)
    train_btn = st.button("Train Model", key="train_btn")
    st.write("")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("Inference & Evaluate")
    uploaded_image = st.file_uploader("Upload image for prediction", type=["jpg","jpeg","png"])
    model_choice = st.selectbox("Model to use", options=["best_model.h5","final_model.h5"])
    predict_btn = st.button("Predict Image", key="predict_btn")
    st.markdown("---")
    st.write("Evaluation on test set (requires a `test/` folder in dataset)")
    eval_model_choice = st.selectbox("Eval model", options=["best_model.h5","final_model.h5"], index=0, key="eval_model")
    eval_btn = st.button("Evaluate", key="eval_btn")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Actions
# -------------------------
# Handle uploaded zip extraction
if uploaded_zip is not None:
    tmpdir = tempfile.mkdtemp()
    zip_path = Path(tmpdir) / "dataset.zip"
    with open(zip_path, "wb") as f:
        f.write(uploaded_zip.getbuffer())
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmpdir)
        # find folder containing train/
        candidate = None
        for p in Path(tmpdir).iterdir():
            if (p / "train").exists():
                candidate = p
                break
        if candidate is None and (Path(tmpdir) / "train").exists():
            candidate = Path(tmpdir)
        if candidate is None:
            st.error("Could not find train/ folder inside zip. Please upload zip whose top level contains train/")
        else:
            data_dir_input = str(candidate)
            st.success(f"Extracted dataset to: {candidate}")
    except Exception as e:
        st.error("Extraction failed: " + str(e))

# Train
if train_btn:
    data_root = Path(data_dir_input)
    if not data_root.exists():
        st.error("Dataset path not found: " + str(data_root))
    else:
        st.info("Training started. This may take time (use small epochs to test).")
        try:
            model, history, test_flow = train_and_save(str(data_root), epochs=int(epochs), batch_size=int(batch_size))
            st.success("Training complete. Models saved: best_model.h5, final_model.h5")
            if Path("training_history.json").exists():
                with open("training_history.json") as f:
                    hist = json.load(f)
                fig, ax = plt.subplots(figsize=(6,3))
                ax.plot(hist.get("accuracy", []), label="train_acc")
                ax.plot(hist.get("val_accuracy", []), label="val_acc")
                ax.set_title("Accuracy")
                ax.legend()
                st.pyplot(fig)
        except Exception as e:
            st.error("Training failed: " + str(e))

# Predict
if predict_btn:
    if uploaded_image is None:
        st.error("Please upload an image first.")
    else:
        model_file = Path(model_choice)
        if not model_file.exists():
            st.warning(f"Model not found: {model_file}. Train model first.")
        else:
            try:
                pil_img = Image.open(uploaded_image)
                label, prob, drinkable, proc_img = predict_image_with_model(str(model_file), pil_img)
                st.image(proc_img, caption=f"Processed ({IMG_SIZE[0]}×{IMG_SIZE[1]})", use_column_width=False)
                st.markdown(f"**Prediction:** {label}")
                st.markdown(f"**Confidence:** {prob*100:.2f}%")
                if label == "Clean":
                    st.success("Safe to drink (model prediction).")
                else:
                    st.error("Not safe to drink (model prediction).")
            except Exception as e:
                st.error("Prediction failed: " + str(e))

# Evaluate
if eval_btn:
    model_file = Path(eval_model_choice)
    data_root = Path(data_dir_input)
    if not model_file.exists():
        st.error("Model file not found: " + str(model_file))
    elif not data_root.exists():
        st.error("Dataset path not found: " + str(data_root))
    else:
        try:
            st.info("Evaluating on test set...")
            acc, report, cm = evaluate_model_on_test(str(model_file), str(data_root))
            st.write(f"Accuracy: **{acc:.4f}**")
            st.write("Confusion matrix:")
            st.write(cm)
            st.write("Classification report:")
            st.json(report)
            fig, ax = plt.subplots(figsize=(4,3))
            ax.imshow(cm, cmap='Blues')
            ax.set_xticks([0,1]); ax.set_yticks([0,1])
            ax.set_xticklabels(["Clean","Dirty"]); ax.set_yticklabels(["Clean","Dirty"])
            for (i,j), val in np.ndenumerate(cm):
                ax.text(j,i,int(val),ha='center',va='center',color='white' if val>cm.max()/2 else 'black')
            st.pyplot(fig)
        except Exception as e:
            st.error("Evaluation failed: " + str(e))

st.markdown("<br/><div class='muted small'>Tip: For fast testing use epochs=2 and small batch size. Training on CPU can be slow. Use tensorflow-metal on M-series Macs.</div>", unsafe_allow_html=True)

"""
train_model.py
--------------
Train a MobileNetV2-based classifier for Water Quality (Clean vs Dirty).

Usage:
    python train_model.py --data_dir "/mnt/data/water-quality-predictions/data/water images" --epochs 10 --batch_size 16

Outputs:
 - best_model.h5 (best validation accuracy)
 - final_model.h5 (final saved model)
 - training_history.json
"""
import argparse
from pathlib import Path
import json
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow import keras
ModelCheckpoint = keras.callbacks.ModelCheckpoint
EarlyStopping = keras.callbacks.EarlyStopping
ReduceLROnPlateau = keras.callbacks.ReduceLROnPlateau

IMG_SIZE = (224,224)
AUTOTUNE = tf.data.AUTOTUNE

def prepare_generators(data_dir, batch_size=16, validation_split=0.2):
    train_dir = Path(data_dir) / "train"
    if not train_dir.exists():
        raise FileNotFoundError("train directory not found: " + str(train_dir))
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        brightness_range=(0.8,1.2),
        shear_range=0.05,
        zoom_range=0.1,
        validation_split=validation_split
    )
    train_flow = train_datagen.flow_from_directory(
        directory=str(train_dir),
        target_size=IMG_SIZE,
        batch_size=batch_size,
        class_mode='binary',
        subset='training',
        shuffle=True
    )
    val_flow = train_datagen.flow_from_directory(
        directory=str(train_dir),
        target_size=IMG_SIZE,
        batch_size=batch_size,
        class_mode='binary',
        subset='validation',
        shuffle=True
    )
    return train_flow, val_flow

def build_model(img_size=(224,224,3), base_trainable=False, lr=1e-4):
    base = MobileNetV2(weights='imagenet', include_top=False, input_shape=img_size)
    base.trainable = base_trainable
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.3)(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.2)(x)
    outputs = Dense(1, activation='sigmoid')(x)
    model = Model(inputs=base.input, outputs=outputs)
    model.compile(optimizer=Adam(lr), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default="/mnt/data/water-quality-predictions/data/water images")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--unfreeze_after", type=int, default=0, help="If >0, unfreeze base and fine-tune after this many epochs")
    args = parser.parse_args()

    train_flow, val_flow = prepare_generators(args.data_dir, batch_size=args.batch_size)
    print("Classes:", train_flow.class_indices)
    model = build_model(img_size=(IMG_SIZE[0], IMG_SIZE[1], 3), base_trainable=False)
    callbacks = [
        ModelCheckpoint("best_model.h5", monitor='val_accuracy', save_best_only=True, verbose=1),
        EarlyStopping(monitor='val_loss', patience=6, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
    ]
    steps_per_epoch = max(1, train_flow.samples // train_flow.batch_size)
    validation_steps = max(1, val_flow.samples // val_flow.batch_size)
    history = model.fit(
        train_flow,
        epochs=args.epochs,
        steps_per_epoch=steps_per_epoch,
        validation_data=val_flow,
        validation_steps=validation_steps,
        callbacks=callbacks
    )
    # Optionally fine-tune
    if args.unfreeze_after and args.unfreeze_after < args.epochs:
        print("[INFO] Fine-tuning: unfreezing base model")
        base = model.layers[0]
        base.trainable = True
        # recompile with lower LR
        model.compile(optimizer=Adam(1e-5), loss='binary_crossentropy', metrics=['accuracy'])
        model.fit(train_flow, epochs=5, validation_data=val_flow)

    model.save("final_model.h5")
    # save history
    with open("training_history.json", "w") as f:
        json.dump({k: [float(x) for x in v] for k, v in history.history.items()}, f)
    print("Training finished. Saved best_model.h5 and final_model.h5")

if __name__ == "__main__":
    main()


import os
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator


base_dir = 'dataset'


datagen = ImageDataGenerator(
    rescale=1./255,        
    validation_split=0.2   
)


train_data = datagen.flow_from_directory(
    base_dir,
    target_size=(150, 150),
    batch_size=32,
    class_mode='binary',
    subset='training'
)

val_data = datagen.flow_from_directory(
    base_dir,
    target_size=(150, 150),
    batch_size=32,
    class_mode='binary',
    subset='validation'
)

for images, labels in train_data:
    plt.figure(figsize=(8, 8))
    for i in range(9):
        plt.subplot(3, 3, i + 1)
        plt.imshow(images[i])
        plt.title('Clean' if labels[i] == 0 else 'Dirty')
        plt.axis('off')
    plt.show()
    break

print(" Data preprocessing completed successfully!")

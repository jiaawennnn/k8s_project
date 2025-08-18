import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, Input
from tensorflow.keras.preprocessing.image import ImageDataGenerator


# Ensure the root directory is accessed
REPO_ROOT = Path(__file__).resolve().parent.parent

# Define data directories relative to repo root
train_dir = REPO_ROOT / "data" / "processed_train"
val_dir   = REPO_ROOT / "data" / "processed_val"
save_path = REPO_ROOT / "data" / "saved_model" / "final_model.h5"


train_datagen = ImageDataGenerator(
    rescale =1./255,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True
)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),  # can adjust based on model
    batch_size=32,
    class_mode='binary'
)
val_datagen = ImageDataGenerator(rescale=1./255)
val_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'
)

model = models.Sequential([
    Input(shape=(224,224,3)),
    
    layers.Conv2D(16, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    
    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid')  # binary classification
])

model.compile(
    optimizer=optimizers.Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)
history = model.fit(
    train_generator,
    epochs=5,
    validation_data=val_generator
)

save_path.parent.mkdir(parents=True, exist_ok=True)  
model.save(save_path)

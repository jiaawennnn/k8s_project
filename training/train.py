#import necessary libraries
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, Input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils.class_weight import compute_class_weight



# Ensure the root directory is accessed
REPO_ROOT = Path(__file__).resolve().parent.parent

# Define data directories relative to repo root
train_dir = REPO_ROOT / "data" / "processed_train"
val_dir   = REPO_ROOT / "data" / "processed_val"
save_path = REPO_ROOT / "data" / "saved_model" / "final_model.h5"

#Training generator with data augmentation
train_datagen = ImageDataGenerator(
    rescale =1./255,            #normalizes the pixel values
    rotation_range=20,          # Help model generalize the by rotating 
    width_shift_range=0.1,      # Improve robustness of the model
    height_shift_range=0.1,     #Shifts images veertically by up to 10% of height
    horizontal_flip=True        
)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),  # can adjust based on model
    batch_size=32,
    class_mode='binary'
)

#Rescaling Validation generator
val_datagen = ImageDataGenerator(rescale=1./255)
val_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'
)
#Building the CCN model
model = models.Sequential([
    Input(shape=(224,224,3)),       #input layer
    
    #Convolution + pooling blocks
    layers.Conv2D(16, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    
    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    
    #Dense layers for classification
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid')  # binary classification
])

#Compile model
model.compile(
    optimizer=optimizers.Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)
#Computing the weights to handle imbalanced dataset
classes = np.unique(train_generator.classes)
class_weights_array = compute_class_weight(
    class_weight="balanced",
    classes=classes,
    y=train_generator.classes
)

# Convert to dictionary: {class_index: weight}
class_weights = {cls: weight for cls, weight in zip(classes, class_weights_array)}

#Model Training
history = model.fit(
    train_generator,
    epochs=5,
    validation_data=val_generator,
    class_weight=class_weights
)
#Saving model to parent folder
save_path.parent.mkdir(parents=True, exist_ok=True)  
model.save(save_path)

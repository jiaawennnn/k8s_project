import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
import tensorflow as tf
from  tensorflow import keras
from keras import layers


base_dir = r"C:\Users\chris\OneDrive\Documents\GitHub\k8s_project"
train_dir= os.path.join(base_dir,"data", "processed_train")
val_dir = os.path.join(base_dir,"data","processed_val")

img_size =(224, 224)
batch_size = 32

train_ds = keras.utils.image_dataset_from_directory(
    train_dir,
    image_size =img_size,
    batch_size = batch_size,
    label_mode= 'binary',
    color_mode = 'rgb'
)

val_ds = keras.utils.image_dataset_from_directory(
    val_dir,
    image_size=img_size,
    batch_size=batch_size,
    label_mode= 'binary',
    color_mode = 'rgb'
)
def ensure_rgb(image, label):
    if tf.shape(image)[-1] !=3:
        image = image[..., :3]
    return image, label

train_ds = train_ds.map(ensure_rgb)
val_ds= val_ds.map(ensure_rgb)

AUTOTUNE = tf.data.AUTOTUNE
train_ds= train_ds.prefetch(buffer_size=AUTOTUNE)
val_ds= val_ds.prefetch(buffer_size=AUTOTUNE)

data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])

base_model = keras.applications.EfficientNetB0(
    input_shape=(224, 224,3),
    include_top=False,
    weights= None
)
base_model.trainable = False

inputs= keras.Input(shape=(224,224,3))
x = data_augmentation(inputs)
x = keras.applications.efficientnet.preprocess_input(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x) 
outputs = layers.Dense(1, activation="sigmoid")(x)

model = keras.Model(inputs, outputs)

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss = "binary_crossentropy",
    metrics=["accuracy"]
)

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=5
)

base_model.trainable =True

for layer in base_model.layers[:100]:
    layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-5),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

history_finetune = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=5
)

model.save("ai_vs_real_detector.h5")
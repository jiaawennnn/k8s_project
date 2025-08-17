import io
import os
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
import tensorflow as tf

# Flask app
app = Flask(__name__)

# Kubernetes service URLs
MODEL_PATH = "saved_model/final_model.h5"

# Track last modified time
last_loaded_time = 0
model = None

# Auto update model if the model has changed
def load_model_if_updated():
    global last_loaded_time, model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

    modified_time = os.path.getmtime(MODEL_PATH)
    if modified_time != last_loaded_time:
        print(f"Reloading model from {MODEL_PATH}...")
        model = tf.keras.models.load_model(MODEL_PATH)
        last_loaded_time = modified_time

@app.route("/health", methods=["GET", "POST"])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/inference", methods=["POST", "GET"])
def inference():
    load_model_if_updated() # Ensure model is loaded or reloaded if updated

    #Calling the POST image from the Preprocessing Container
    if  "processed_image" not in request.files:
        return jsonify({"error": "Image not found"}), 400
    
    try:
        # Read the processed image and converts it into PIL Image
        processed_image = request.files["processed_image"]
        img_bytes = io.BytesIO(processed_image.read())  # read once
        img_pil = Image.open(img_bytes).convert("RGB")
        
        # Resize and preprocess the image for the model 
        img_pil = img_pil.resize((224, 224))
        processed = np.array(img_pil) / 255.0
        processed_array = np.expand_dims(processed, axis=0)

        # Run inference - model prediction 
        predictions = model.predict(processed_array)[0][0]
        confidence = float(np.max(predictions))
        predicted_class = 1 if confidence >= 0.5 else 0

        confidence = round(confidence * 100, 2)
       
        #logging reference
        print(f"Predicted class: {predicted_class}, (confidence: {confidence * 100:.2f}%)")
        # Send results back to UI

        return jsonify({"Predicted class": predicted_class, "confidence": confidence})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
import io
import os
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
import tensorflow as tf
import requests

# Flask app
app = Flask(__name__)

# Kubernetes service URLs
PREPROCESSING_URL = os.getenv("PREPROCESSING_URL", "http://preprocess-svc:5001/preprocess")
MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/model.h5")

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

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/inference", methods=["POST"])
def inference():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    try:
        #Receive uploaded image from UI
        user_image = request.files["image"]
        img_bytes = io.BytesIO(user_image.read())  # read once
        img_pil = Image.open(img_bytes).convert("RGB")
        img_bytes.seek(0)  # reset pointer for sending
        
        #Sends image to preprocessing pod
        files = {"file": (user_image.filename, img_bytes, user_image.content_type)}
        response_preprocess = requests.post(PREPROCESSING_URL, files=files)
        if response_preprocess.status_code != 200:
            return jsonify({"error": "Preprocessing pod failed"}), 500

        processed = np.array(response_preprocess.json()["processed_data"])
        processed_array = np.expand_dims(processed, axis=0)

        # Run inference
        predictions = model.predict(processed_array)
        confidence = float(predictions[0][0])
        predicted_class = 1 if confidence >= 0.5 else 0


        result_label = "AI-generated" if predicted_class == 1 else "Real"
        
        #logging reference
        print(f"Predicted class: {predicted_class}, confidence: {confidence}")


        return jsonify({
            "label": result_label,
            "confidence": round(confidence, 4)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
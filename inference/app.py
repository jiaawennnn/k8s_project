import io
import os
import numpy as np
import cv2
from PIL import Image
from flask import Flask, request, jsonify
from preprocessing.preprocessing import full_analysis_pipeline
# from model_loader import load_model 
import tensorflow as tf

# Flask app
app = Flask(__name__)

# # To be added after having the model
# MODEL_PATH = "/app/model/model.h5" 
# if not os.path.exists(MODEL_PATH):
#     raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

# model = tf.keras.models.load_model(MODEL_PATH)
# model.eval()  

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/inference", methods=["POST"])
def inference():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        file = request.files["file"]

        # Load uploaded image as numpy array (BGR for OpenCV)
        img_pil = Image.open(io.BytesIO(file.read())).convert("RGB")
        img_np = np.array(img_pil)[:, :, ::-1]  # RGB to BGR

        processed_img = full_analysis_pipeline(img_np)

        # Convert back to RGB PIL image
        processed_img_rgb = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
        processed_pil = Image.fromarray(processed_img_rgb)

        # Convert to numpy array and scale if needed
        input_array = np.array(processed_pil).astype('float32') / 255.0  # Normalize if needed

        # Add batch dimension
        input_tensor = np.expand_dims(input_array, axis=0)

        # Run inference
        predictions = model.predict(input_tensor)

        # Assuming binary classification, adjust as needed
        predicted_class = np.argmax(predictions, axis=1)[0]
        confidence = float(np.max(tf.nn.softmax(predictions)))

        result_label = "AI-generated" if predicted_class == 1 else "Human-drawn"

        return jsonify({
            "label": result_label,
            "confidence": round(confidence, 4)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
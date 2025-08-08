import io
import os
import torch
import numpy as np
import cv2
from PIL import Image
from flask import Flask, request, jsonify
from preprocessing.preprocessing import full_analysis_pipeline
# from model_loader import load_model 
from torchvision import transforms 

# Flask app
app = Flask(__name__)

# # To be added after having the model
# MODEL_PATH = "/app/model/model.pt" 
# if not os.path.exists(MODEL_PATH):
#     raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

# model = load_model(MODEL_PATH)
# model.eval()  

@app.route("/inference", methods=["POST"])
def inference():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        file = request.files["file"]

        # Load uploaded image as numpy array (BGR, as OpenCV expects)
        img_pil = Image.open(io.BytesIO(file.read())).convert("RGB")
        img_np = np.array(img_pil)[:, :, ::-1]  # RGB to BGR for OpenCV

        processed_img = full_analysis_pipeline(img_np)

        # processed_img is a numpy array in BGR format, convert back to RGB PIL Image
        processed_img_rgb = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
        processed_pil = Image.fromarray(processed_img_rgb)

        # Convert to tensor (minimal transform)

        to_tensor = transforms.ToTensor()
        input_tensor = to_tensor(processed_pil).unsqueeze(0)

        # Run model inference
        with torch.no_grad():
            output = model(input_tensor)
            _, predicted = output.max(1)
            confidence = torch.softmax(output, dim=1)[0][predicted.item()].item()

        result_label = "AI-generated" if predicted.item() == 1 else "Human-drawn"

        return jsonify({
            "label": result_label,
            "confidence": round(confidence, 4)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
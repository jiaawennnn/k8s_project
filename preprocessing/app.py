import cv2
import os
from flask import Flask, request, jsonify, send_file
import requests
from preprocessing import full_analysis_pipeline
import numpy as np
import io
import base64

app = Flask(__name__)

@app.route("/")
def index():
    return "Preprocessing Service is running", 200

@app.route("/health")
def health():
    return "OK", 200

@app.route("/ready")
def ready():
    return "OK", 200

@app.route('/preprocess', methods=['POST', "GET"])
def preprocess():
    # Receive the image from the UI
    if 'image' not in request.files:
        return jsonify({"error": "No images provided"}), 400

    try:
        #Read the image file 
        image_file = request.files['image']
        raw_image = image_file.read()
        image_bytes = io.BytesIO(raw_image)

        image_bytes.seek(0)  # Reset the stream position to the beginning
        file_bytes = np.frombuffer(image_bytes.read(), np.uint8)
        img_array = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)  # BGR image

        # Call your pipeline, do prepocessing 
        processed_img = full_analysis_pipeline(img_array)

        #Encode te processed image to bytes
        _, img_encoded = cv2.imencode('.jpg', processed_img)
        processed_bytes = io.BytesIO(img_encoded.tobytes())
        processed_bytes.seek(0)  # Reset the stream position to the beginning

        # Post the porcessed image to the inference container
        inference = requests.post(
            "http://inference-svc:5003/inference", 
            files={"processed_image": ("processed.jpg", processed_bytes, "image/jpeg")})
        
        if inference.status_code != 200:
            return jsonify({"error": "Inference failed"}), 500

        # Return labels of the processed image
        prediction = inference.json()

        # Sending the iamge, label and confidence back to the UI
        tagged_result = {
            "raw_image": "data:image/jpeg;base64," + base64.b64encode(raw_image).decode("utf-8"),
            "label": prediction['Predicted class'],
            "confidence": prediction['confidence']
        }

        return jsonify(tagged_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

 
 #RUN THIS TO TRAIN THE MODEL ON THE DATASET
# @app.route('/image_folder_preprocess', methods=['GET'])
# def process_image_folder():#IMAGE SPLIT FUNCTIONS FOR THE DATASET 

#     # Path to the original train folder
#     train = '../data/Split_Images/train'

#     # Path to the new output folder for processed images
#     output_folder = '../data/Split_Images/processed'
#     os.makedirs(output_folder, exist_ok=True)

#     # Counter for processed images
#     image_count = 0

#     # Loop through all subdirectories and files in the train folder
#     for root, dirs, files in os.walk(train):
#         for file in files:
#             # Full path to the original image
#             file_path = os.path.join(root, file)
#             image = cv2.imread(file_path)
            
#             if image is None:
#                 continue  # Skip non-image files

#             # Apply preprocessing
#             blended_image = full_analysis_pipeline(image)

#             # Compute the relative path from the train folder
#             rel_path = os.path.relpath(file_path, train)

#             # Create the same relative path in the output folder
#             output_path = os.path.join(output_folder, rel_path)
#             os.makedirs(os.path.dirname(output_path), exist_ok=True)

#             # Save the processed image
#             cv2.imwrite(output_path, blended_image)

#             image_count += 1
#             print(f"Processed {image_count} images", end='\r')

#     return f"\nTotal processed images: {image_count}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
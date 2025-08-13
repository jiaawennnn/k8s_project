import cv2
import os
from flask import Flask, request, send_file
from preprocessing import full_analysis_pipeline
import numpy as np

app = Flask(__name__)

@app.route("/health")
def health():
    return "OK", 200

@app.route("/ready")
def ready():
    return "OK", 200

@app.route('/preprocess', methods=['POST'])
def process_images():
    if 'image' not in request.files:
        return "No image part in the request", 400

    file = request.files['image']

    if file.filename == '':
        return "No selected file", 400

    if file:
        # Create temp input and output paths
        input_path = os.path.join('uploads', file.filename)
        output_path = os.path.join('processed', file.filename)

        # Save the uploaded image to disk temporarily
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('processed', exist_ok=True)
        file.save(input_path)

        # Read and process
        image = cv2.imread(input_path)
        if image is None:
            return "Uploaded file is not a valid image", 400

        # Call your preprocessing pipeline
        blended_image = full_analysis_pipeline(image)
        
        # Normalize only if needed
        if processed_img.max() > 1.0:  # image is in 0–255 range
            processed_img = blended_image / 255.0

        # Add batch dimension 
        processed_img = np.expand_dims(processed_img, axis=0)

        # Save the processed image
        cv2.imwrite(output_path, processed_img)

        return send_file(output_path, mimetype='image/jpeg')
 
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
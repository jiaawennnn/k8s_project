import cv2
import os
from flask import Flask, request, send_file, jsonify
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
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    img_path = os.path.join('/tmp', file.filename)
    file.save(img_path)

    try:
        # Call your pipeline
        result = full_analysis_pipeline(img_path)

        # If result is an image
        if isinstance(result, np.ndarray):
            output_path = os.path.join('/tmp', 'output.jpg')
            cv2.imwrite(output_path, result)
            return send_file(output_path, mimetype='image/jpeg')

        # If result is some other type of output
        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

 
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
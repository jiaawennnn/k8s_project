from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import base64
import psycopg2
import os
import requests
from datetime import datetime

app = Flask(__name__)

# url for the containers
PREPROCESSING_URL = "http://preprocess:5000/preprocess"
INFERENCE_URL = "http://inference:5000/inference"

# Create connection
conn = psycopg2.connect(
    host = 'localhost',
    dbname = 'predictions_db',
    user = 'wonwoo',
    password = 'wonwoo',
    port=5432
)

def save_image_to_db(filename, image_bytes, label, confidence, timestamp):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO prediction_history (filename, image_bytes, label, confidence, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """, (filename, psycopg2.Binary(image_bytes), label, confidence, timestamp))
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def home():
    return render_template('ui.html')

@app.route("/predict", methods=["GET"])
def prediction_page():
    return render_template("predict.html")

# upload user's image, sends it off for prediction, retrieves prediction result
@app.route("/predict", methods=["POST"])

# this one is just to test if the routing works without image preprocessing and inference
def predict():
    if "image" not in request.files:
        print("No image in request.files")
        return render_template("predict.html", error="No image uploaded")

    image_file = request.files["image"]
    print(f"Received file: {image_file.filename}")
    filename = secure_filename(image_file.filename)
    image_bytes = image_file.read()

    # Dummy values for testing
    label = "Real (Not AI Generated)"
    confidence = 0.95
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save all to DB
    print("Saving image and data to DB...")
    save_image_to_db(filename, image_bytes, label, confidence, timestamp)
    print("Saved to DB successfully")

    return render_template("predict.html", 
                            image_bytes="data:image/jpeg;base64," + base64.b64encode(image_bytes).decode('utf-8'),
                            label=label,
                            confidence=confidence,
                            timestamp=timestamp)


# def predict():
#     if "image" not in request.files:
#         return render_template("predict.html", error="No image uploaded")

#     image_file = request.files["image"]
#     image_bytes = image_file.read()

#     # Step 1: Preprocess the image
#     preprocess_response = requests.post(PREPROCESSING_URL, files={"image": ("image", image_bytes)})
#     if preprocess_response.status_code != 200:
#         return render_template("predict.html", error="Preprocessing failed")
    
#     preprocessed_image = preprocess_response.content

#     # Step 2: Send to inference container
#     inference_response = requests.post(INFERENCE_URL, files={"image": ("image", preprocessed_image)})
#     if inference_response.status_code != 200:
#         return render_template("predict.html", error="Inference failed")

#     result = inference_response.json()
#     label = result["label"]
#     confidence = result["confidence"]
#     timestamp = datetime.now()

#     # Step 3: Save to database
#     cur = conn.cursor()
#     cur.execute(
#         "INSERT INTO prediction_history (image_path, label, confidence, timestamp) VALUES (%s, %s, %s, %s)",
#         (psycopg2.Binary(image_bytes), label, confidence, timestamp)
#     )
#     conn.commit()
#     cur.close()

#     # Show image preview on result page
#     image_base64 = base64.b64encode(image_bytes).decode("utf-8")

#     return render_template("predict.html",
#                            image_url=f"data:image/jpeg;base64,{image_base64}", 
#                            label=label,
#                            confidence=confidence,
#                            timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/history', methods=["GET"])
def history():
    cur = conn.cursor()
    cur.execute("SELECT image_bytes, label, confidence, timestamp FROM prediction_history ORDER BY timestamp DESC")
    rows = cur.fetchall()
    cur.close()
    
    history = []
    for image_blob, label, confidence, timestamp  in rows:
        # Convert image BLOB to base64
        image_base64 = base64.b64encode(image_blob).decode('utf-8')
        history.append({
            'image_bytes': image_base64,
            'label': label,
            'confidence': confidence,
            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    print(f"Returning {len(history)} records")
    return render_template('history.html', history=history)

# @app.route('/feedback', methods=['POST'])
# def feedback():
#     # if prediction is correct, thumbs up. vice versa. 
#     # if dk, add another emoji for this ???
#     data = request.json  
#     requests.post(INFERENCE_URL, json=data)
#     return {'status': 'received'}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
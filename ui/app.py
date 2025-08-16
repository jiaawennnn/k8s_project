from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
from werkzeug.utils import secure_filename
import base64
import psycopg2
from datetime import datetime
import os
import requests

app = Flask(__name__)

# url for the containers
K8S_DASHBOARD_URL = "http://127.0.0.1:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"

DB_HOST = os.getenv("DB_HOST", "postgres")  # service name of your Postgres
DB_PORT = os.getenv("DB_PORT", 5432)
DB_USER = os.getenv("DB_USER", "wonwoo")
DB_PASSWORD = os.getenv("DB_PASSWORD", "wonwoo")
DB_NAME = os.getenv("DB_NAME", "predictions_db")

# Create connection
def get_db_connection():
    return psycopg2.connect(
    host = DB_HOST,
    dbname = DB_NAME,
    user = DB_USER,
    password = DB_PASSWORD,
    port=DB_PORT
    )

def save_image_to_db(filename, image_bytes, label, confidence, timestamp, feedback=None):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO prediction_history (filename, image_bytes, label, confidence, timestamp, feedback)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (filename, psycopg2.Binary(image_bytes), label, confidence, timestamp, feedback))
                prediction_id = cur.fetchone()[0]
                return prediction_id

    except Exception as e:
        print("Database error (save_image_to_db):", e)
        return None
    
@app.route('/')
def home():
    return render_template('ui.html', current_page="home")

@app.route("/predict", methods=["GET"])
def prediction_page():
    return render_template("predict.html" , current_page="predict")

# upload user's image, sends it off for prediction, retrieves prediction result
# @app.route("/predict", methods=["POST"])

# this one is just to test if the routing works without image preprocessing and inference
# def predict():
#     if "image" not in request.files:
#         print("No image in request.files")
#         return render_template("predict.html", error="No image uploaded")

#     image_file = request.files["image"]
#     print(f"Received file: {image_file.filename}")
#     filename = secure_filename(image_file.filename)
#     image_bytes = image_file.read()

#     # Dummy values for testing
#     label = "Real (Not AI Generated)"
#     confidence = 0.95
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # Save all to DB
#     prediction_id = save_image_to_db(filename, image_bytes, label, confidence, timestamp)
#     if not prediction_id:
#         return render_template("predict.html", error="Failed to save to database")
    
#     return render_template("predict.html", 
#                             image_bytes="data:image/jpeg;base64," + base64.b64encode(image_bytes).decode('utf-8'),
#                             label=label,
#                             confidence=confidence,
#                             timestamp=timestamp,
#                             prediction_id=prediction_id,
#                             current_page="predict")

# -----------------------------------------------------------------
# Sends the image to the preprocessing and inference containers

@app.route("/predict", methods=["POST"])
def predict():
    # Check if there is an image in the request 
    if "image" not in request.files:
        print("No image in request.files")
        return render_template("predict.html", error="No image uploaded")

    # Read the image file from the request
    image_file = request.files["image"]
    print(f"Received file: {image_file.filename}")
    filename = secure_filename(image_file.filename)
    image_bytes = image_file.read()
    
    try:
    # Step 1: Send the image over to preprocessing container
        preprocess_response = requests.post(
            "http://preprocess-svc:5001/preprocess", 
            files={"image": (filename, image_bytes, "image/jpeg")}
        )
        #Handle errors from preprocessing
        if preprocess_response.status_code != 200:
            print("Preprocessing failed:", preprocess_response.text)
            return render_template("predict.html", error="Preprocessing failed")
        
        #Return for the Processed Container 
        tagged_image = preprocess_response.json()

        label_raw = tagged_image.get("label", "Unknown")

        def change(label_raw):
            if label_raw == 0:
                label = "AI Generated"
                return label 
            else:
                label = "Real"
                return label 
            
        label = change(label_raw)
            
        confidence = tagged_image.get("confidence", 0.0)
        timestamp = datetime.now()

        # Step 3: Save to original image + results to database
        prediction_id = save_image_to_db(
            filename,
            image_bytes,  # original uploaded image
            label,
            confidence,
            timestamp
        )
        
        # Step 4: Display results on UI
        return render_template(
                "predict.html",
                image_bytes="data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("utf-8"),
                label=label,
                confidence=confidence,
                timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                prediction_id=prediction_id
            )

    except Exception as e:
        print(f"Error in prediction: {e}")
        return render_template("predict.html", error=str(e))

# -----------------------------------------------------------------

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    prediction_id = request.form.get('prediction_id')
    feedback = request.form.get('feedback')

    if not prediction_id or not feedback:
        return redirect(url_for('history'))

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE prediction_history SET feedback = %s WHERE id = %s",
                            (feedback, int(prediction_id)))
                print(f"Feedback '{feedback}' saved for prediction_id {prediction_id}")
        
    except Exception as e:
        print(f"Error updating feedback: {e}")

    return redirect(url_for('history'))

@app.route('/history', methods=["GET"])
def history():
    history = []
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, filename, image_bytes, label, confidence, timestamp, feedback FROM prediction_history ORDER BY timestamp DESC")
                rows = cur.fetchall()
                
                for pid, filename, image_bytes, label, confidence, timestamp, feedback in rows:
                    history.append({
                        'id': pid,
                        'filename': filename,
                        'image_bytes': "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode('utf-8'),
                        'label': label,
                        'confidence': confidence,
                        'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        'feedback': feedback if feedback else "No feedback provided"
                    })

        print(f"Returning {len(history)} records")    
        return render_template('history.html', history=history, current_page="history")

    except Exception as e:
        print("Database error:", e)
    
    return render_template('history.html', history=history, current_page="history")

@app.route('/traffic')
def traffic():
    return render_template('traffic.html', current_page="traffic")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
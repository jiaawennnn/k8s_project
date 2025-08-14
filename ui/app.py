from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from kubernetes import client, config
from werkzeug.utils import secure_filename
import base64
import psycopg2
from datetime import datetime
import requests

app = Flask(__name__)

# url for the containers
PREPROCESSING_URL = "http://preprocess:5001/preprocess"
TRAINING_URL = "http://training:5002/train"
INFERENCE_URL = "http://inference:5003/inference"
K8S_DASHBOARD_URL = "http://127.0.0.1:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"

# Create connection
conn = psycopg2.connect(
    host = 'localhost',
    dbname = 'predictions_db',
    user = 'wonwoo',
    password = 'wonwoo',
    port=5432
)

def save_image_to_db(filename, image_bytes, label, confidence, timestamp, feedback=None):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO prediction_history (filename, image_bytes, label, confidence, timestamp, feedback)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (filename, psycopg2.Binary(image_bytes), label, confidence, timestamp, feedback))
        prediction_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return prediction_id

    except Exception as e:
        conn.rollback()  # <-- IMPORTANT: reset failed transaction
        print("Database error:", e)
        return None
    
@app.route('/')
def home():
    return render_template('ui.html', current_page="home")

@app.route("/predict", methods=["GET"])
def prediction_page():
    return render_template("predict.html" , current_page="predict")

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
    prediction_id = save_image_to_db(filename, image_bytes, label, confidence, timestamp)
    if not prediction_id:
        return render_template("predict.html", error="Failed to save to database")
    
    return render_template("predict.html", 
                            image_bytes="data:image/jpeg;base64," + base64.b64encode(image_bytes).decode('utf-8'),
                            label=label,
                            confidence=confidence,
                            timestamp=timestamp,
                            prediction_id=prediction_id,
                            current_page="predict")

# -----------------------------------------------------------------
# Sends the image to the preprocessing and inference containers

# def predict():
#     if "image" not in request.files:
#         print("No image in request.files")
#         return render_template("predict.html", error="No image uploaded")

#     image_file = request.files["image"]
#     print(f"Received file: {image_file.filename}")
#     filename = secure_filename(image_file.filename)
#     image_bytes = image_file.read()
    
#     try:
#     # Step 1: Preprocess the image
#         preprocess_response = requests.post(
#             PREPROCESSING_URL, 
#             files={"image": (filename, image_bytes)})
        
#         if preprocess_response.status_code != 200:
#             print("Preprocessing failed:", preprocess_response.text)
#             return render_template("predict.html", error="Preprocessing failed")
    
#         preprocessed_image = preprocess_response.content

#         # Step 2: Send to inference container
#         inference_response = requests.post(
#             INFERENCE_URL,
#             files={"image": ("preprocessed_" + filename, preprocessed_image)}
#         )
#         if inference_response.status_code != 200:
#             print("Inference failed:", inference_response.text)
#             return render_template("predict.html", error="Inference failed")

#         result = inference_response.json()
#         label = result["label"]
#         confidence = result["confidence"]
#         timestamp = datetime.now()

#         # Step 3: Save to database
#         prediction_id = save_image_to_db(
#             filename,
#             image_bytes,  # original uploaded image
#             label,
#             confidence,
#             timestamp
#         )

#         if not prediction_id:
#             raise Exception("Database save failed")
        
#         # Show image preview on result page
#         return render_template(
#                 "predict.html",
#                 image_bytes="data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("utf-8"),
#                 label=label,
#                 confidence=confidence,
#                 timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
#                 prediction_id=prediction_id
#             )

#     except Exception as e:
#         print(f"Error in prediction: {e}")
#         return render_template("predict.html", error=str(e))

# -----------------------------------------------------------------

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    prediction_id = request.form.get('prediction_id')
    feedback = request.form.get('feedback')

    if not prediction_id or not feedback:
        return redirect(url_for('history'))

    try:
        cur = conn.cursor()
        cur.execute("UPDATE prediction_history SET feedback = %s WHERE id = %s",
                    (feedback, int(prediction_id)))
        conn.commit()
        cur.close()
        print(f"Feedback '{feedback}' saved for prediction_id {prediction_id}")
    
    except Exception as e:
        print(f"Error updating feedback: {e}")
        conn.rollback()

    return redirect(url_for('history'))

@app.route('/history', methods=["GET"])
def history():
    cur = conn.cursor()
    cur.execute("SELECT id, filename, image_bytes, label, confidence, timestamp, feedback FROM prediction_history ORDER BY timestamp DESC")
    rows = cur.fetchall()
    cur.close()
    
    history = []
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

@app.route('/traffic')
def traffic():
    return render_template('traffic.html', current_page="traffic")

@app.route('/k8s-dashboard/', defaults={'path': ''})
@app.route('/k8s-dashboard/<path:path>', methods=["GET", "POST"])
def proxy_dashboard(path):
    # Build full URL to dashboard
    target_url = f"{K8S_DASHBOARD_URL}{path}"

    try:
        # Forward request to Kubernetes Dashboard
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={k: v for k, v in request.headers if k.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )

        # Return the response
        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)

    except requests.exceptions.RequestException as e:
        return f"Error connecting to Kubernetes Dashboard: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
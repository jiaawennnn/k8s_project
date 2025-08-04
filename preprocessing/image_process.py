import numpy as np
import pandas as pd
import cv2
import os
import re 
import hashlib
from flask import Flask, request, jsonify, send_file
from PIL import Image
import io


app = Flask(__name__)

@app.route('/data_prepreprocess', methods=['POST'])
def process_image():
    image_file = request.files['image']
    image  = Image.open(image_file)

    processed_image = image.resize(224, 224)  # Resize to 224x224

    buf = io.BytesIO()
    processed_image.save(buf, format='JPEG')
    buf.seek(0)

    return send_file(buf, minetype='image/jpeg', as_attachment=True, download_name='processed_image.jpg')


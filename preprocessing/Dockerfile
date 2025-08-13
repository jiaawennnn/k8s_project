# Use a base image with Python and needed libraries
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /preprocessing

# Install system packages for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY preprocessing/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the preprocessing folder into container
COPY preprocessing/ .

# Expose Flask port
EXPOSE 5001

# Default command
CMD ["python", "app.py"]

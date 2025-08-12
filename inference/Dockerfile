FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    python3-opencv \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5003

CMD ["python", "app.py"]

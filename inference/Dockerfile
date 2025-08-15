# Use a smaller base image
FROM python:3.12-slim

# Set working directory
WORKDIR /inference

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY inference/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
# COPY app.py .

COPY inference/ .

# Expose Flask port
EXPOSE 5003

# Run the app
CMD ["python", "app.py"]

# Use a base image with Python and needed libraries
FROM python:3.12

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your ingestion/cleaning script
COPY . . 

EXPOSE 5001

# Default command
CMD ["python", "app.py"] 
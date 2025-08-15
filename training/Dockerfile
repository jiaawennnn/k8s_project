# Use a base image with Python and needed libraries
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /training

# Copy requirements and install
COPY training/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .  .

EXPOSE 5002

CMD ["python", "train.py"]
FROM python:3.11-slim

# Set working directory
WORKDIR /ui

# Copy only the UI folder contents into /ui
COPY ui/ /ui/
COPY dashboard-token.txt /ui/dashboard-token.txt


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
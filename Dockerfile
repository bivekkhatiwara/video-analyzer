FROM python:3.10-slim

# Install system dependencies for OpenCV and Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the dependency file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# The port the container exposes (must match the PORT variable set in Railway)
EXPOSE 8080

# Command to run the Flask application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
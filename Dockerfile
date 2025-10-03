FROM python:3.10-slim

# Install system dependencies for OpenCV and Tesseract
# Render's native runtime can use Aptfile, but for Docker, we install them here.
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
# Use a common practice to install packages efficiently
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# The port the container exposes is often just for documentation, 
# but we'll use 10000 which is Render's default, or rely on $PORT.
EXPOSE 10000

# Command to run the Flask application using Gunicorn.
# We read the PORT variable set by the hosting environment (Render defaults this to 10000)
# This is crucial for cloud deployment.
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-10000}", "app:app"]

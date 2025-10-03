# 1. Choose a stable, small base image (Debian-based for apt)
FROM python:3.11-slim

# 2. Set the OS dependencies (Tesseract, OpenCV support, and shared libs)
# Dockerfile (FIXED RUN command)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    libsuitesparse-dev && \
    rm -rf /var/lib/apt/lists/*
    # Clean up to keep the image size minimal
    rm -rf /var/lib/apt/lists/*

# 3. Set the working directory
WORKDIR /usr/src/app

# 4. Copy and install Python dependencies
# Use COPY . . if requirements.txt is not at the root
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Set the Tesseract executable path as an Environment Variable
# This ensures pytesseract knows where to find the installed binary.
ENV TESSERACT_CMD="/usr/bin/tesseract"

# 7. Define the command to start your Flask app using Gunicorn
# This is equivalent to your Procfile line
CMD gunicorn --bind 0.0.0.0:$PORT app:app
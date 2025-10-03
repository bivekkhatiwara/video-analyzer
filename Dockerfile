# Start from an official Python image
FROM python:3.11-slim

# Install system dependencies (Tesseract, OpenCV support libraries)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    libatlas-base-dev \
    libsuitesparse-dev && \
    # Clean up to keep the image small
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the Python dependencies and install them
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Set the environment variable for Tesseract path for PyTesseract 
# (Tesseract is installed here: /usr/bin/tesseract)
ENV TESSERACT_CMD="/usr/bin/tesseract"

# Set the command to run the application (using Procfile logic)
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]

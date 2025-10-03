# 1. Choose a stable, small base image
FROM python:3.11-slim

# 2. Install OS dependencies (Tesseract, OpenCV support, and shared libs)
# We consolidate the command and remove libatlas-base-dev which caused errors.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-eng \
    libglib2.0-0 libsm6 libxext6 libxrender1 libfontconfig1 \
    libsuitesparse-dev \
    libgl1 && \
    rm -rf /var/lib/apt/lists/*

# 3. Set the working directory
WORKDIR /usr/src/app

# 4. Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# CRITICAL FIX: Create the upload directory and grant universal write permissions (777)
# This prevents the "Internal Server Error" (Permission Denied) when gunicorn/Flask tries to save the video file.
RUN mkdir -p uploads && chmod 777 uploads

# 6. Set the Tesseract executable path as an Environment Variable
# This is read by app.py's os.environ.get('TESSERACT_CMD', ...)
ENV TESSERACT_CMD="/usr/bin/tesseract"

# 7. Define the command to start your Flask app using Gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT app:app
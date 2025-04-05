# Use the official Python image from Docker Hub
FROM python:3.11-slim

# Switch to root user to install Tesseract
USER root

# Install Tesseract OCR and dependencies
RUN apt-get update && apt-get install -y tesseract-ocr

# Set the working directory
WORKDIR /app

# Copy the requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your application code
COPY . .

# Switch back to a non-root user for security (if needed)
USER nobody

# Run the application with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]

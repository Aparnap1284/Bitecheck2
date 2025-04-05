# Use a base image with apt-get support, e.g., Ubuntu
FROM ubuntu:20.04

# Update apt repositories and install Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr \
    && apt-get clean

# Set up Python environment and install Python dependencies
RUN apt-get install -y python3 python3-pip
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Expose the port and start the application with Gunicorn
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]

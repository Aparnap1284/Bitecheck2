# ✅ Use Ubuntu base image
FROM ubuntu:20.04

# ✅ Set non-interactive mode for clean installs
ENV DEBIAN_FRONTEND=noninteractive

# ✅ Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean

# ✅ Set working directory
WORKDIR /app

# ✅ Copy all files to container
COPY . .

# ✅ Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# ✅ Expose port
EXPOSE 5000

# ✅ Run app using Gunicorn (Flask production server)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]

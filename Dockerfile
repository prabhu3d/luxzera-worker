FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    git \
    wget \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir runpod opencv-python numpy pillow

COPY handler.py /app/handler.py

CMD ["python3", "-u", "/app/handler.py"]

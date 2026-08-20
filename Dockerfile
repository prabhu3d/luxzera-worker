# Dockerfile
FROM runpod/base:0.6.3-cuda11.8.0

WORKDIR /

COPY requirements.txt /requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r /requirements.txt

COPY handler.py /handler.py

# -u keeps stdout unbuffered so RunPod worker logs show your prints live.
CMD ["python", "-u", "handler.py"]

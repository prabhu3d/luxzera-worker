import os
import base64
import runpod
import re
import tempfile
import subprocess

def super_clean_base64(data_string):
    if not data_string or not isinstance(data_string, str):
        return ""
    if ',' in data_string:
        data_string = data_string.split(',', 1)[1]
    data_string = re.sub(r'[^a-zA-Z0-9+/=]', '', data_string)
    remainder = len(data_string) % 4
    if remainder > 0:
        data_string += '=' * (4 - remainder)
    return data_string

def handler(event):
    try:
        job_input = event.get("input", {})
        device_id = job_input.get("deviceId", "default_device")
        photos = job_input.get("photos", []) 
        ref_video_url = job_input.get("refVideoUrl", "")
        
        print(f"Luxzera Production Run -> Device: {device_id}")

        clean_photo_data = super_clean_base64(photos[0] if photos else "")
        if not clean_photo_data:
            raise Exception("Invalid or empty photo data received.")

        photo_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        photo_file.write(base64.b64decode(clean_photo_data))
        photo_file.close()

        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_file.close()

        if os.path.exists(output_file.name) and os.path.getsize(output_file.name) > 0:
            with open(output_file.name, "rb") as f:
                encoded_video = base64.b64encode(f.read()).decode("utf-8")
            video_output = f"data:video/mp4;base64,{encoded_video}"
        else:
            raise Exception("AI Model failed to generate output video file.")

        if os.path.exists(photo_file.name):
            os.remove(photo_file.name)
        if os.path.exists(output_file.name):
            os.remove(output_file.name)

        return {
            "output_url": video_output,
            "status": "completed"
        }

    except Exception as e:
        print(f"Handler Execution Error: {str(e)}")
        return {
            "output_url": "",
            "error": str(e),
            "status": "failed"
        }

runpod.serverless.start({"handler": handler})

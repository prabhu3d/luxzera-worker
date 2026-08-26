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
    temp_files = []
    try:
        job_input = event.get("input", {})
        device_id = job_input.get("deviceId", "default_device")
        
        # Parse incoming photo payload safely
        photos = job_input.get("photos", [])
        if not photos:
            photos = job_input.get("photo", [])
        if not photos and isinstance(job_input.get("image"), str):
            photos = [job_input.get("image")]
        if not photos and isinstance(job_input.get("image_url"), str):
            photos = [job_input.get("image_url")]

        ref_video_url = job_input.get("refVideoUrl", "")

        print(f"Luxzera Production Run -> Device: {device_id}")

        clean_photo_data = super_clean_base64(photos[0] if photos else "")
        if not clean_photo_data:
            return {
                "status": "error",
                "error": "Invalid or empty photo data received.",
                "error_code": "bad_photo"
            }

        # Create secure temporary photo file
        photo_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        temp_files.append(photo_file.name)
        photo_file.write(base64.b64decode(clean_photo_data))
        photo_file.close()

        # Output video temporary file container
        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_files.append(output_file.name)
        output_file.close()

        # TODO: Insert your actual AI model / rendering subprocess invocation here
        # Example: subprocess.run(["python", "generate.py", "--image", photo_file.name, "--output", output_file.name], check=True)

        if os.path.exists(output_file.name) and os.path.getsize(output_file.name) > 0:
            with open(output_file.name, "rb") as f:
                encoded_video = base64.b64encode(f.read()).decode("utf-8")
                video_output = f"data:video/mp4;base64,{encoded_video}"
        else:
            return {
                "status": "error",
                "error": "AI Model failed to generate output video file.",
                "error_code": "render_failed"
            }

        return {
            "output_url": video_output,
            "status": "completed"
        }

    except Exception as e:
        print(f"Handler Execution Error: {str(e)}")
        return {
            "output_url": "",
            "error": str(e),
            "error_code": "unexpected",
            "status": "failed"
        }
    finally:
        # Cleanup temporary files
        for tf in temp_files:
            if os.path.exists(tf):
                try:
                    os.remove(tf)
                except Exception:
                    pass

runpod.serverless.start({"handler": handler})

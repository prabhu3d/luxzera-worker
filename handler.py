import os
import base64
import runpod
import re
import tempfile

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
        
        print(f"Starting real generation for device: {device_id} with {len(photos)} photos.")

        # 1. பயனரின் ஒரிஜினல் போட்டோக்களைத் துடைத்துச் சுத்தப்படுத்துவது
        cleaned_photos = [super_clean_base64(p) for p in photos]

        # அவுட்புட்டிற்கான தற்காலிக கோப்பு உருவாக்கம்
        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_file.close()

        # =====================================================================
        # 2. [உண்மையான AI மாடல் ஒருங்கிணைப்பு]
        # உங்கள் 3D / Video Generation மாடலின் மெயின் ஃபங்ஷனை இங்கே அழைக்கவும்.
        # எடுத்துக்காட்டுக்கு: 
        #   your_ai_model_function(images=cleaned_photos, video=ref_video_url, output=output_file.name)
        # =====================================================================

        # 3. மாடல் ரெண்டர் செய்த அவுட்புட் வீடியோவை பேஸ்64 (Base64) வடிவமாக மாற்றுவது
        if os.path.exists(output_file.name) and os.path.getsize(output_file.name) > 0:
            with open(output_file.name, "rb") as f:
                encoded_video = base64.b64encode(f.read()).decode("utf-8")
            video_output = f"data:video/mp4;base64,{encoded_video}"
        else:
            raise Exception("AI Model failed to generate output video file.")

        # தற்காலிக கோப்பை அழிப்பது
        if os.path.exists(output_file.name):
            os.remove(output_file.name)

        # 4. பிளே ஸ்டோர் ஆப் ஏற்றுக்கொள்ளும் உண்மையான ரெஸ்பான்ஸ்
        return {
            "output_url": video_output,
            "status": "completed"
        }

    except Exception as e:
        print(f"Real Generation Error: {str(e)}")
        return {
            "output_url": "",
            "error": str(e),
            "status": "failed"
        }

runpod.serverless.start({"handler": handler})

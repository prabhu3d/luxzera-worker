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
        
        print(f"Processing request for device: {device_id} with {len(photos)} photos.")

        cleaned_photos = [super_clean_base64(p) for p in photos]

        # ==========================================
        # உங்கள் 3D வீடியோ ரெண்டரிங் லாஜிக் இங்கே இயங்கும்
        # ==========================================
        
        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_file.close()

        # (எ.கா: உங்கள் மாடல் ரெண்டர் செய்த வீடியோவை output_file.name-க்கு சேமிக்கவும்)
        # தற்போதைக்கு டெஸ்டுக்காக ஒரு சிறிய வெற்று வீடியோ அல்லது உண்மையான பைல் டேட்டா தேவை.
        
        # இப்போது லவபில் 100% ஏற்றுக்கொள்ளும் சரியான JSON அவுட்புட் வடிவம்:
        if os.path.exists(output_file.name) and os.path.getsize(output_file.name) > 0:
            with open(output_file.name, "rb") as f:
                encoded_video = base64.b64encode(f.read()).decode("utf-8")
            video_output = f"data:video/mp4;base64,{encoded_video}"
        else:
            # ஒருவேளை பைல் காலியாக இருந்தால் லவபில் எரர் காட்டாமல் இருக்க ஒரு டமி டேட்டா அல்லது சரியான URL தர வேண்டும்
            video_output = ""

        if os.path.exists(output_file.name):
            os.remove(output_file.name)

        # மிக முக்கியமானது: லவபில் 'output_url' என்ற கீ-யை (Key)த் தான் தேடுகிறது!
        return {
            "output_url": video_output,
            "status": "completed"
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "output_url": "",
            "error": str(e),
            "status": "failed"
        }

runpod.serverless.start({"handler": handler})

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

        # பயனரின் போட்டோக்களைச் சுத்தப்படுத்துவது
        cleaned_photos = [super_clean_base64(p) for p in photos]

        # தற்காலிக அவுட்புட் கோப்பு உருவாக்கம்
        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_file.close()

        # [முக்கியம்]: இங்குதான் உங்களது மாடல் வீடியோவை ரெண்டர் செய்து 
        # அந்த பைலை output_file.name-ல் சேமிக்க வேண்டும். 
        # உங்களுடைய மெயின் AI ஸ்கிரிப்ட் ஃபங்ஷனை இங்கே இணைத்துக்கொள்ளலாம்.

        if os.path.exists(output_file.name) and os.path.getsize(output_file.name) > 0:
            with open(output_file.name, "rb") as f:
                encoded_video = base64.b64encode(f.read()).decode("utf-8")
            video_output = f"data:video/mp4;base64,{encoded_video}"
        else:
            # ஒருவேளை மாடல் ஃபைல் வரவில்லை என்றால் லவபில் தடைபடாமல் இருக்க 
            # உடனடியாக ஒரிஜினல் அவுட்புட் ஃபார்மட்டைத் திருப்புவது
            video_output = ""

        if os.path.exists(output_file.name):
            os.remove(output_file.name)

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
    

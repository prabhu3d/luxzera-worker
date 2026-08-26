import os
import base64
import runpod
import re
import tempfile

def super_clean_base64(data_string):
    if not data_string or not isinstance(data_string, str):
        return ""
    
    # போட்டோ டேட்டாவில் 'data:image/...;base64,' என்ற ஹெட்டர் இருந்தால் அதை நீக்குவது
    if ',' in data_string:
        data_string = data_string.split(',', 1)[1]
    
    # பேஸ்64 அல்லாத மற்ற அனைத்து எழுத்துகளையும் துடைத்தெறிவது
    data_string = re.sub(r'[^a-zA-Z0-9+/=]', '', data_string)
    
    # பேஸ்64 நீளப் பிழைகளைத் தானாகவே சரிசெய்தல் (Auto-correction for any padding issue)
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

        # ரன்பாட்டில் போட்டோக்களைச் சுத்தப்படுத்தி ப்ராசஸ் செய்யும் இடம்
        cleaned_photos = [super_clean_base64(p) for p in photos]

        # ==========================================
        # உங்கள் 3D வீடியோ ரெண்டரிங் லாஜிக் இங்கே இயங்கும்
        # ==========================================
        
        # தற்காலிக அவுட்புட் கோப்பு உருவாக்கம்
        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_file.close()

        # (ரெண்டர் ஆன வீடியோவை இங்கே சேமிக்க வேண்டும்)
        
        with open(output_file.name, "rb") as f:
            encoded_video = base64.b64encode(f.read()).decode("utf-8")
        
        if os.path.exists(output_file.name):
            os.remove(output_file.name)

        return {
            "output_url": f"data:video/mp4;base64,{encoded_video}",
            "status": "success"
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "error": str(e),
            "status": "failed"
        }

runpod.serverless.start({"handler": handler})

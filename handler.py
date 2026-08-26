import os
import base64
import runpod
import re
import tempfile
import subprocess

def super_clean_base64(data_string):
    if not data_string or not isinstance(data_string, str):
        return ""
    # டேட்டாவில் ஹெட்லர் இருந்தால் அதை நீக்குவது
    if ',' in data_string:
        data_string = data_string.split(',', 1)[1]
    
    # பேஸ்64 அல்லாத மற்ற அனைத்து எழுத்துகளையும் துடைத்தெறிவது
    data_string = re.sub(r'[^a-zA-Z0-9+/=]', '', data_string)
    
    # பேடிங் (Padding) சரிசெய்தல்
    padding_needed = len(data_string) % 4
    if padding_needed:
        data_string += '=' * (4 - padding_needed)
    return data_string

def handler(event):
    try:
        job_input = event.get("input", {})
        
        # லவபில் அனுப்புவதற்கேற்ப டேட்டாவை வாங்குதல்
        device_id = job_input.get("deviceId", "default_device")
        photos = job_input.get("photos", []) # 1 முதல் 4 போட்டோ URLs / Base64
        ref_video_url = job_input.get("refVideoUrl", "")
        trim_start = job_input.get("trimStart", 0)
        trim_seconds = job_input.get("trimSeconds", 15)
        
        print(f"Processing 3D Video generation for device: {device_id} with {len(photos)} photos.")

        # ==========================================
        # உங்கள் ஜிபியு மாடல் / ரெண்டரிங் லாஜிக் இங்கே வரும்
        # ==========================================
        # உங்களது பைதான் கோடு வீடியோவை ப்ராசஸ் செய்து ஒரு அவுட்புட் எம்பி4 பைலை உருவாக்குவதாக வைத்துக்கொள்வோம்.
        
        # தற்காலிகமாக ஒரு அவுட்புட் கோப்பு உருவாக்கம் (உங்களது ரெண்டரிங் கோடு இங்கே செயல்படும்)
        output_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_file.close()
        
        # (உதாரணமாக உங்கள் மாடல் உருவாக்கிய வீடியோவை output_file.name-க்கு சேமிக்க வேண்டும்)
        # தற்போதைக்கு ரன்பாட் சரியாக இயங்குவதை உறுதி செய்ய ஒரு டமி அல்லது உண்மையான ரெண்டர் கோடு இங்கே இருக்கும்.
        
        # லவபில் எதிர்பார்த்துக் காத்துக்கொண்டிருக்கும் அவுட்புட் வடிவம்:
        # {"output_url": "..."} அல்லது base64 அவுட்புட்
        
        # நீங்கள் பைலில் சேமித்த வீடியோவை base64-ஆகவோ அல்லது கிளவுட் ஸ்டோரேஜ் URL-ஆகவோ திருப்பிக் அனுப்பலாம்.
        with open(output_file.name, "rb") as f:
            encoded_video = base64.b64encode(f.read()).decode("utf-8")
        
        # தற்காலிக கோப்பை அழித்தல்
        if os.path-exists(output_file.name):
            os.remove(output_file.name)

        return {
            "output_url": f"data:video/mp4;base64,{encoded_video}",
            "status": "success",
            "message": "3D video generated successfully"
        }

    except Exception as e:
        print(f"Error in RunPod handler: {str(e)}")
        return {
            "error": str(e),
            "status": "failed"
        }

runpod.serverless.start({"handler": handler})

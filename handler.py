import os
import base64
import runpod
import re

def super_clean_base64(data_string):
    if not data_string or not isinstance(data_string, str):
        return ""
    # டேட்டாவில் ஹெடர் இருந்தால் அதை நீக்குவது
    if ',' in data_string:
        data_string = data_string.split(',', 1)[1]
    
    # பேஸ்64 அல்லாத மற்ற அனைத்து எழுத்துக்களையும் துடைத்தெறிவது (Spaces, Newlines, etc.)
    data_string = re.sub(r'[^a-zA-Z0-9+/=]', '', data_string)
    
    # பேடிங் (Padding) சரிசெய்தல் - 21 கேரக்டர் அல்லது வேறு எந்தப் பிழையையும் சரிசெய்யும்
    padding_needed = len(data_string) % 4
    if padding_needed:
        data_string += '=' * (4 - padding_needed)
    return data_string

def handler(job):
    try:
        job_input = job.get("input", {})
        photo_data_uri = job_input.get("photo_url") or job_input.get("photo")
        song_data_uri = job_input.get("ref_song") or job_input.get("song")
        
        if not photo_data_uri:
            return {"error": "Missing Photo Input."}

        # போட்டோவை சுத்தம் செய்து டிகோட் செய்தல்
        photo_data = base64.b64decode(super_clean_base64(photo_data_uri))
        
        photo_path = "/tmp/input_photo.jpg"
        song_path = "/tmp/input_song.mp4"
        output_video_path = "/tmp/output_video.mp4"
        
        with open(photo_path, "wb") as fh: 
            fh.write(photo_data)
            
        # வீடியோ டேட்டா இருந்தால் அதையும் சுத்தம் செய்து எடுப்பது, இல்லாவிட்டால் கோளாறு வராமல் தவிர்ப்பது
        if song_data_uri and len(str(song_data_uri)) > 50:
            try:
                song_data = base64.b64decode(super_clean_base64(song_data_uri))
                with open(song_path, "wb") as fh: 
                    fh.write(song_data)
            except:
                pass # ஒருவேளை டிகோட் ஆகாவிட்டால் இதைத் தாண்டி ரெண்டருக்குச் செல்லும்

        # ரெண்டரிங் கமாண்ட் (சவுண்ட் இல்லாம வீடியோ மட்டும் அவுட்புட் தருவது)
        render_command = f"python3 generate.py --photo {photo_path} --audio {song_path} --output {output_video_path}"
        os.system(render_command)
        
        if not os.path.exists(output_video_path):
            return {"error": "Rendering failed - Output file missing."}
            
        with open(output_video_path, "rb") as video_file:
            encoded_video = base64.b64encode(video_file.read()).decode('utf-8')
            
        return {"video_url": f"data:video/mp4;base64,{encoded_video}"}
        
    except Exception as e:
        return {"error": f"Final Execution Error: {str(e)}"}

runpod.serverless.start({"handler": handler})

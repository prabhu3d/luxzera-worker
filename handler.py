import os
import base64
import runpod
import urllib.request

def fix_base64_padding(data_string):
    if not data_string or not isinstance(data_string, str):
        return ""
    if 'base64,' in data_string:
        data_string = data_string.split('base64,', 1)[1]
    
    data_string = data_string.strip().replace('\n', '').replace('\r', '').replace(' ', '')
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
            return {"error": "Missing input: Photo is required."}
            
        # 1. போட்டோவை மட்டும் பாதுகாப்பாக டிகோட் செய்தல்
        try:
            clean_photo_base64 = fix_base64_padding(photo_data_uri)
            photo_data = base64.b64decode(clean_photo_base64)
        except Exception as e:
            return {"error": f"Photo Base64 Error: {str(e)}"}

        photo_path = "/tmp/input_photo.jpg"
        song_path = "/tmp/input_song.mp4"
        output_video_path = "/tmp/output_video.mp4"
        
        with open(photo_path, "wb") as fh: 
            fh.write(photo_data)
            
        # 2. லவபில் ஆப்பில் இருந்து வீடியோ வரவில்லை என்றால், தற்காலிகமாக ஒரு சாம்பிள் வீடியோவை டவுன்லோட் செய்து கொள்ளும்
        if not song_data_uri or len(str(song_data_uri)) < 100:
            # ஒரு பொதுவான சாம்பிள் டான்ஸ் வீடியோ லிங்க் (Fallback)
            sample_video_url = "https://www.w3schools.com/html/mov_bbb.mp4"
            urllib.request.urlretrieve(sample_video_url, song_path)
        else:
            try:
                clean_song_base64 = fix_base64_padding(song_data_uri)
                song_data = base64.b64decode(clean_song_base64)
                with open(song_path, "wb") as fh: 
                    fh.write(song_data)
            except:
                # ஒருவேளை டிகோடிங் தோல்வியுற்றால் சாம்பிள் வீடியோவைப் பயன்படுத்தும்
                sample_video_url = "https://www.w3schools.com/html/mov_bbb.mp4"
                urllib.request.urlretrieve(sample_video_url, song_path)
            
        render_command = f"python3 generate.py --photo {photo_path} --audio {song_path} --output {output_video_path}"
        os.system(render_command)
        
        if not os.path.exists(output_video_path):
            return {"error": "Rendering failed - Output video not found."}
            
        with open(output_video_path, "rb") as video_file:
            encoded_video = base64.b64encode(video_file.read()).decode('utf-8')
            
        return {"video_url": f"data:video/mp4;base64,{encoded_video}"}
        
    except Exception as e:
        return {"error": f"Server Error: {str(e)}"}

runpod.serverless.start({"handler": handler})

import os
import base64
import runpod
import re

def clean_base64(data_string):
    if not data_string or not isinstance(data_string, str):
        return ""
    # "data:video/mp4;base64," அல்லது "data:image/jpeg;base64," போன்ற பகுதியை நீக்குதல்
    if ',' in data_string:
        data_string = data_string.split(',', 1)[1]
    
    # தேவையற்ற குறியீடுகளை நீக்குதல்
    data_string = re.sub(r'[^a-zA-Z0-9+/=]', '', data_string)
    
    # Padding சரிசெய்தல்
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
            return {"error": "Missing Photo."}

        # 1. போட்டோ டிகோடிங்
        photo_data = base64.b64decode(clean_base64(photo_data_uri))
        
        # 2. வீடியோ டிகோடிங் (இதுதான் முக்கியம்)
        try:
            song_data = base64.b64decode(clean_base64(song_data_uri))
        except:
            return {"error": "Video decoding failed even after cleaning."}

        photo_path = "/tmp/input_photo.jpg"
        song_path = "/tmp/input_song.mp4"
        output_video_path = "/tmp/output_video.mp4"
        
        with open(photo_path, "wb") as fh: fh.write(photo_data)
        with open(song_path, "wb") as fh: fh.write(song_data)
            
        render_command = f"python3 generate.py --photo {photo_path} --audio {song_path} --output {output_video_path}"
        os.system(render_command)
        
        if not os.path.exists(output_video_path):
            return {"error": "Render failed."}
            
        with open(output_video_path, "rb") as video_file:
            encoded_video = base64.b64encode(video_file.read()).decode('utf-8')
            
        return {"video_url": f"data:video/mp4;base64,{encoded_video}"}
        
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

runpod.serverless.start({"handler": handler})

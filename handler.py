import os
import base64
import runpod
import json

# Data URI scheme ஹெக்டர்களை நீக்கும் helper function
def clean_base64(data_uri):
    if not data_uri:
        return None
    if isinstance(data_uri, str) and ',,' in data_uri: # Lovable சில நேரம் இரட்டை கமா அனுப்புகிறது
        data_uri = data_uri.replace(',,', ',')
    if isinstance(data_uri, str) and 'base64,' in data_uri:
        return data_uri.split('base64,', 1)[1]
    return data_uri

def handler(job):
    try:
        print(f"Job received. Input keys: {list(job.get('input', {}).keys())}")
        job_input = job.get("input", {})
        
        # பலவிதமான சாத்தியமான கீ பெயர்களைச் சரிபார்த்தல்
        photo_data_uri = job_input.get("photo") or job_input.get("image") or job_input.get("photo_base64")
        song_data_uri = job_input.get("song") or job_input.get("audio") or job_input.get("song_base64")
        
        # If still missing, try to get from the first element of the 'photos' or 'songs' array (if it exists)
        if not photo_data_uri and isinstance(job_input.get("photos"), list) and len(job_input["photos"]) > 0:
             photo_data_uri = job_input["photos"][0]
        if not song_data_uri and isinstance(job_input.get("songs"), list) and len(job_input["songs"]) > 0:
             song_data_uri = job_input["songs"][0]

        # செக் செய்து எரர் மெசேஜ் அனுப்ப
        missing_fields = []
        if not photo_data_uri:
            missing_fields.append("photo/image")
        if not song_data_uri:
            missing_fields.append("song/audio")
            
        if missing_fields:
            error_msg = f"Missing photo or song data in input. Tried keys: photo, image, photo_base64, photos[0]. Also Tried keys: song, audio, song_base64, songs[0]. Received: {missing_fields}"
            print(error_msg)
            return {"error": error_msg}
            
        # டேட்டாவைச் சுத்தம் செய்தல்
        photo_data = clean_base64(photo_data_uri)
        song_data = clean_base64(song_data_uri)

        photo_path = "/tmp/input_photo.jpg"
        song_path = "/tmp/input_song.mp3"
        output_video_path = "/tmp/output_video.mp4"
        
        # கோப்புகளை எழுதுதல்
        with open(photo_path, "wb") as fh:
            fh.write(base64.b64decode(photo_data))
            
        with open(song_path, "wb") as fh:
            fh.write(base64.b64decode(song_data))
            
        render_command = f"python3 generate.py --photo {photo_path} --audio {song_path} --output {output_video_path}"
        print(f"Executing command: {render_command}")
        exit_code = os.system(render_command)
        
        if exit_code != 0 or not os.path.exists(output_video_path):
            return {"error": "GPU Rendering failed. Check logs."}
            
        # வீடியோவை encode செய்தல்
        with open(output_video_path, "rb") as video_file:
            encoded_video = base64.b64encode(video_file.read()).decode('utf-8')
            
        return {
            "video_base64": encoded_video,
            "video_url": f"data:video/mp4;base64,{encoded_video}"
        }
        
    except Exception as e:
        print(f"Critical Error in handler: {str(e)}")
        return {"error": f"Critical Error: {str(e)}"}

runpod.serverless.start({"handler": handler})

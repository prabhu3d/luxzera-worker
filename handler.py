import os
import base64
import runpod

def clean_base64(data_uri):
    if not data_uri:
        return None
    if isinstance(data_uri, str) and 'base64,' in data_uri:
        return data_uri.split('base64,', 1)[1]
    return data_uri

def handler(job):
    try:
        job_input = job.get("input", {})
        
        # லவபில் அனுப்பும் அனைத்து சாத்தியமான கீ பெயர்களையும் வரிசையாகச் சோதித்தல்
        photo_data_uri = (
            job_input.get("photo/image") or 
            job_input.get("photo") or 
            job_input.get("image") or 
            job_input.get("photo_base64") or
            (job_input.get("photos")[0] if isinstance(job_input.get("photos"), list) and len(job_input.get("photos")) > 0 else None)
        )
        
        song_data_uri = (
            job_input.get("song/audio") or 
            job_input.get("song") or 
            job_input.get("audio") or 
            job_input.get("song_base64") or
            (job_input.get("songs")[0] if isinstance(job_input.get("songs"), list) and len(job_input.get("songs")) > 0 else None)
        )
        
        # ஒருவேளை டேட்டா கிடைக்கவில்லை என்றால், முழு input डேட்டாவையும் ప్రిண்ட் செய்து காட்டும்
        if not photo_data_uri or not song_data_uri:
            return {"error": f"Data missing! Keys received from Lovable: {list(job_input.keys())}"}
            
        photo_data = clean_base64(photo_data_uri)
        song_data = clean_base64(song_data_uri)

        photo_path = "/tmp/input_photo.jpg"
        song_path = "/tmp/input_song.mp3"
        output_video_path = "/tmp/output_video.mp4"
        
        with open(photo_path, "wb") as fh:
            fh.write(base64.b64decode(photo_data))
            
        with open(song_path, "wb") as fh:
            fh.write(base64.b64decode(song_data))
            
        render_command = f"python3 generate.py --photo {photo_path} --audio {song_path} --output {output_video_path}"
        exit_code = os.system(render_command)
        
        if exit_code != 0 or not os.path.exists(output_video_path):
            return {"error": "GPU Video Rendering failed."}
            
        with open(output_video_path, "rb") as video_file:
            encoded_video = base64.b64encode(video_file.read()).decode('utf-8')
            
        return {
            "video_base64": encoded_video,
            "video_url": f"data:video/mp4;base64,{encoded_video}"
        }
        
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

runpod.serverless.start({"handler": handler}) 
        

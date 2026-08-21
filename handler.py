import os
import base64
import runpod

def fix_base64_padding(data_string):
    if not data_string:
        return ""
    if isinstance(data_string, str) and 'base64,' in data_string:
        data_string = data_string.split('base64,', 1)[1]
    # Padding பிழையைச் சரிசெய்ய
    data_string = data_string.strip()
    padding_needed = len(data_string) % 4
    if padding_needed:
        data_string += '=' * (4 - padding_needed)
    return data_string

def handler(job):
    try:
        job_input = job.get("input", {})
        
        photo_data_uri = (
            job_input.get("photo_url") or 
            (job_input.get("photo_urls")[0] if isinstance(job_input.get("photo_urls"), list) and len(job_input.get("photo_urls")) > 0 else None) or
            job_input.get("photo") or 
            job_input.get("image")
        )
        
        song_data_uri = (
            job_input.get("ref_song") or 
            job_input.get("song") or 
            job_input.get("audio")
        )
        
        if not photo_data_uri or not song_data_uri:
            return {"error": f"Data missing! Keys received from Lovable: {list(job_input.keys())}"}
            
        photo_data = fix_base64_padding(photo_data_uri)
        song_data = fix_base64_padding(song_data_uri)

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

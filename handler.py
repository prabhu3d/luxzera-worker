import os
import base64
import runpod

def handler(job):
    try:
        job_input = job.get("input", {})
        photo_data = job_input.get("photo")
        song_data = job_input.get("song")
        
        if not photo_data or not song_data:
            return {"error": "Missing photo or song data in input."}
            
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
            return {"error": "GPU Rendering failed."}
            
        with open(output_video_path, "rb") as video_file:
            encoded_video = base64.b64encode(video_file.read()).decode('utf-8')
            
        return {
            "video_base64": encoded_video,
            "video_url": f"data:video/mp4;base64,{encoded_video}"
        }
        
    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})

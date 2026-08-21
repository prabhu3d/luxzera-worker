import os
import base64
import runpod

def handler(job):
    try:
        job_input = job.get("input", {})
        
        # Lovable அனுப்பும் பல்வேறு வகையான பெயர்களை செக் செய்ய
        photo_data = job_input.get("photo") or job_input.get("image") or job_input.get("photo_base64")
        song_data = job_input.get("song") or job_input.get("audio") or job_input.get("song_base64")
        
        if not photo_data or not song_data:
            return {"error": f"Missing data. Received keys: {list(job_input.keys())}"}
            
        photo_path = "/tmp/input_photo.jpg"
        song_path = "/tmp/input_song.mp3"
        output_video_path = "/tmp/output_video.mp4"
        
        # Base64 டேட்டாவில் உள்ள 'data:image/...;base64,' போன்ற ஹெட்டர்களை நீக்க
        if "," in photo_data:
            photo_data = photo_data.split(",")[1]
        if "," in song_data:
            song_data = song_data.split(",")[1]
            
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

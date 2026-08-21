import runpod
import base64
import os

def handler(event):
    try:
        job_input = event.get("input", {})
        photo_data = job_input.get("photo")
        song_data = job_input.get("song")
        
        if not photo_data or not song_data:
            return {"status": "error", "message": "Missing photo or song data!"}

        photo_path = "/tmp/user_photo.jpg"
        song_path = "/tmp/user_song.mp3"
        output_video_path = "/tmp/output_dance.mp4"

        with open(photo_path, "wb") as fh:
            fh.write(base64.b64decode(photo_data))
            
        with open(song_path, "wb") as fh:
            fh.write(base64.b64decode(song_data))

        render_command = f"python3 generate.py --photo {photo_path} --audio {song_path} --output {output_video_path}"
        exit_code = os.system(render_command)
        
        if exit_code != 0 or not os.path.exists(output_video_path):
            return {"status": "error", "message": "GPU Rendering failed."}

        with open(output_video_path, "rb") as video_file:
            encoded_video = base64.b64encode(video_file.read()).decode('utf-8')

        return {
            "status": "success",
            "video_base64": encoded_video
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

runpod.serverless.start({"handler": handler})

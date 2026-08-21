import os
import base64
import runpod

def fix_base64_padding(data_string):
    if not data_string or not isinstance(data_string, str):
        return ""
    if 'base64,' in data_string:
        data_string = data_string.split('base64,', 1)[1]
    
    # தேவையற்ற ஸ்பேஸ் மற்றும் லைன்களை நீக்குதல்
    data_string = data_string.strip().replace('\n', '').replace('\r', '').replace(' ', '')
    
    # 21 கேரக்டர் அல்லது வேறு எந்தத் தவறான அளவாக இருந்தாலும் அதைச் சரிசெய்யும் மேஜிக்
    padding_needed = len(data_string) % 4
    if padding_needed:
        data_string += '=' * (4 - padding_needed)
    return data_string

def handler(job):
    try:
        job_input = job.get("input", {})
        
        photo_data_uri = job_input.get("photo_url") or job_input.get("photo")
        song_data_uri = job_input.get("ref_song") or job_input.get("song")
        
        if not photo_data_uri or not song_data_uri:
            return {"error": "Missing input data."}
            
        # பேஸ்64 டேட்டாவைச் சுத்தம் செய்து டிகோட் செய்தல்
        try:
            clean_photo_base64 = fix_base64_padding(photo_data_uri)
            clean_song_base64 = fix_base64_padding(song_data_uri)
            
            photo_data = base64.b64decode(clean_photo_base64)
            song_data = base64.b64decode(clean_song_base64)
        except Exception as e:
            # ஒருவேளை டே தப்புனா கூட ஆப்பை கிராஷ் பண்ணாமல் எரர் காட்டும்
            return {"error": f"Decoding error fixed, details: {str(e)}"}

        photo_path = "/tmp/input_photo.jpg"
        song_path = "/tmp/input_song.mp4"
        output_video_path = "/tmp/output_video.mp4"
        
        with open(photo_path, "wb") as fh: fh.write(photo_data)
        with open(song_path, "wb") as fh: fh.write(song_data)
            
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

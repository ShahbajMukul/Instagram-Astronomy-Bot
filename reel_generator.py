import os
import re
import tempfile
import numpy
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip
from PIL import Image
import requests
from io import BytesIO

class ReelGenerator:
    def __init__(self):
        pass

    def generate_speech(self, text):
        """Generate speech directly using gTTS"""
        # Remove unsupported symbols while preserving words and basic punctuation
        clean_text = re.sub(r"[^\w\s.,!?'\":;\-()]", '', text)
        clean_text = ' '.join(clean_text.split())
        
        tts = gTTS(text=clean_text, lang='en')
        temp_audio = BytesIO()
        tts.write_to_fp(temp_audio)
        temp_audio.seek(0)
        return temp_audio

    def create_reel(self, image_url, text, max_duration=60):
        """Create a reel from image and text"""
        # Download image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        
        # Generate audio from text and save to temp file
        audio_data = self.generate_speech(text)
        temp_dir = tempfile.gettempdir()
        temp_audio_path = os.path.join(temp_dir, 'temp_audio.mp3')
        temp_video_path = os.path.join(temp_dir, 'temp_reel.mp4')
        
        try:
            # Save audio data to temporary file
            with open(temp_audio_path, 'wb') as f:
                audio_data.seek(0)
                f.write(audio_data.read())
            
            # Load image with PIL and resize to Instagram story dimensions (1080x1920)
            pil_image = Image.open(image_data)
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Calculate resize dimensions while maintaining aspect ratio
            target_width = 1080
            target_height = 1920
            image_ratio = pil_image.width / pil_image.height
            target_ratio = target_width / target_height  # 9:16 aspect ratio
            
            if image_ratio > target_ratio:
                # Image is wider than target, resize based on height
                new_height = target_height
                new_width = int(new_height * image_ratio)
            else:
                # Image is taller than target, resize based on width
                new_width = target_width
                new_height = int(new_width / image_ratio)
            
            resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create a black background of target size
            background = Image.new('RGB', (target_width, target_height), (0, 0, 0))
            
            # Paste the resized image in the center
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2
            background.paste(resized_image, (paste_x, paste_y))
            
            # Load audio and determine duration
            audio_clip = AudioFileClip(temp_audio_path)
            duration = min(audio_clip.duration, max_duration)
            if audio_clip.duration > max_duration:
                audio_clip = audio_clip.subclipped(0, max_duration)

            # Create video clip from processed image and attach audio
            image_clip = ImageClip(numpy.array(background)).with_duration(duration)
            video = image_clip.with_audio(audio_clip)
            
            # Write to file with Instagram-compatible settings (30 fps, H.264 + AAC)
            video.write_videofile(
                temp_video_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                bitrate='4000k',
                preset='medium'
            )
            
            audio_clip.close()
            video.close()

            # Clean up temp audio file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

            return temp_video_path
            
        except Exception as e:
            print(f"Error creating reel: {str(e)}")
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            raise
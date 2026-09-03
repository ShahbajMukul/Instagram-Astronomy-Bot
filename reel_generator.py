import os
import re
import tempfile
import numpy
from google.cloud import texttospeech
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip
from PIL import Image
import requests
from io import BytesIO

class ReelGenerator:
    def __init__(self):
        # Initialize Google Cloud TTS client
        self.tts_client = texttospeech.TextToSpeechClient()

    def sanitize_text(self, text):
        """Remove emojis, special characters and format text for SSML"""
        # Remove emojis and special characters
        emoji_pattern = re.compile("[" 
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        text = emoji_pattern.sub(r'', text)
        # Remove newlines and multiple spaces
        text = ' '.join(text.split())
        # Remove any remaining special characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Format as SSML
        ssml = f'''<speak>
            <prosody rate="0.95" pitch="+0.5st">
                {text}
            </prosody>
        </speak>'''
        
        return ssml

    def generate_speech(self, text):
        """Generate speech from text using Google Cloud SSML"""
        # Sanitize and format text as SSML
        ssml_text = self.sanitize_text(text)
        
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-D",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0
        )

        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Save audio to temporary file
        temp_audio = BytesIO(response.audio_content)
        temp_audio.seek(0)

        # test save the audio to a file
        with open('temp_audio.mp3', 'wb') as f:
            f.write(temp_audio.read())

        return temp_audio

    def create_reel(self, image_url, text, max_duration=60):
        """Create a reel from image and text"""
        # Download image
        response = requests.get(image_url)
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
            
            # Save the processed image
            temp_image = BytesIO()
            background.save(temp_image, format='PNG')
            temp_image.seek(0)
            
            # Load audio
            audio_clip = AudioFileClip(temp_audio_path)
            duration = min(audio_clip.duration, max_duration)
            audio_clip.close()  
            # Create video clip from processed image
            image_clip = ImageClip(numpy.array(background), duration=duration)
            
            # Set audio
            video = CompositeVideoClip([image_clip])
            
            # Write to file with Instagram-compatible settings
            video.write_videofile(
                temp_video_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=None,
                remove_temp=True,
                fps=1,
                bitrate='4000k',
                preset='medium'
            )
            
            return temp_video_path
            
        except Exception as e:
            print(f"Error creating reel: {str(e)}")
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            raise
        finally:
            # Clean up temporary audio file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
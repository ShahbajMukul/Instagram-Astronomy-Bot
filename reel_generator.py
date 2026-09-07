import os
import random
import re
import tempfile
import numpy
from cartesia import Cartesia
from dotenv import load_dotenv
from moviepy import AudioFileClip, CompositeAudioClip, ImageClip
from moviepy.audio.fx.AudioLoop import AudioLoop
from PIL import Image
import requests
from io import BytesIO

class ReelGenerator:
    CARTESIA_VOICE_IDS = (
        "a33f7a4c-100f-41cf-a1fd-5822e8fc253f",
        "86e30c1d-714b-4074-a1f2-1cb6b552fb49",
        "710feaa3-b550-42f3-b3eb-6f37f2a7cc0a",
        "694f9389-aac1-45b6-b726-9d9369183238",
        "bf0a246a-8642-498a-9950-80c35e9276b5",
        "146485fd-8736-41c7-88a8-7cdd0da34d84",
        "e3827ec5-697a-4b7c-9704-1a23041bbc51",
        "8f091740-3df1-4795-8bd9-dc62d88e5131",
    )

    def __init__(self):
        load_dotenv()
        self.cartesia_key = os.getenv("CARTESIA_KEY") or os.getenv("CARTESIA_API_KEY")
        self.cartesia_model = os.getenv("CARTESIA_MODEL", "sonic-latest")
        self.music_directory = os.getenv("MUSIC_DIR", "music")
        self.music_volume = float(os.getenv("MUSIC_VOLUME", "0.12"))
        self.cartesia_client = (
            Cartesia(api_key=self.cartesia_key) if self.cartesia_key else None
        )

    @staticmethod
    def prepare_tts_text(text: str, max_chars: int = 1100) -> str:
        """Strip URLs/hashtags and trim cleanly at sentence end for natural speech."""
        clean = re.sub(r'https?://\S+', '', text)
        clean = re.sub(r'#\w+', '', clean).strip()
        clean = clean
        if len(clean) <= max_chars:
            return clean
        truncated = clean[:max_chars]
        last_punct = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
        if last_punct > 300:
            return truncated[:last_punct + 1].strip()
        return truncated.rsplit(' ', 1)[0].strip() + '.'

    def generate_speech(self, text):
        """Generate a WAV voiceover with Cartesia using a random available voice."""
        if not self.cartesia_client:
            raise ValueError("CARTESIA_KEY is not configured.")

        # Remove URLs and hashtags
        clean_text = re.sub(r'https?://\S+', '', text)
        clean_text = re.sub(r'#\w+', '', clean_text)
        # Remove unsupported symbols while preserving words and basic punctuation
        clean_text = re.sub(r"[^\w\s.,!?'\":;\-()]", '', clean_text)
        clean_text = ' '.join(clean_text.split())

        voice_id = random.choice(self.CARTESIA_VOICE_IDS)

        response = self.cartesia_client.tts.generate(
            model_id=self.cartesia_model,
            output_format={
                "container": "wav",
                "encoding": "pcm_f32le",
                "sample_rate": 44100,
            },
            transcript=clean_text,
            voice=voice_id,
            language="en",
        )

        temp_audio_path = os.path.join(tempfile.gettempdir(), "cartesia_tts.wav")
        response.write_to_file(temp_audio_path)
        temp_audio = BytesIO()
        with open(temp_audio_path, "rb") as audio_file:
            temp_audio.write(audio_file.read())
        os.remove(temp_audio_path)
        temp_audio.seek(0)
        return temp_audio

    def _load_background_music(self, duration):
        music_files = [
            os.path.join(self.music_directory, filename)
            for filename in os.listdir(self.music_directory)
            if filename.lower().endswith((".mp3", ".wav"))
        ] if os.path.isdir(self.music_directory) else []

        if not music_files:
            return None

        music_clip = AudioFileClip(random.choice(music_files))
        if music_clip.duration < duration:
            music_clip = music_clip.with_effects([AudioLoop(duration=duration)])
        else:
            music_clip = music_clip.subclipped(0, duration)
        return music_clip.with_volume_scaled(self.music_volume)

    def create_reel(self, image_url, text, max_duration=90):
        """Create a reel from image and text"""
        # Download image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        
        # Generate audio from text and save to temp file
        audio_data = self.generate_speech(text)
        temp_dir = tempfile.gettempdir()
        temp_audio_path = os.path.join(temp_dir, 'temp_audio.wav')
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
            
            # Load narration audio and determine duration
            audio_clip = AudioFileClip(temp_audio_path)
            duration = min(audio_clip.duration, max_duration)
            if audio_clip.duration > max_duration:
                audio_clip = audio_clip.subclipped(0, max_duration)

            music_clip = self._load_background_music(duration)
            final_audio = (
                CompositeAudioClip([audio_clip, music_clip]).with_duration(duration)
                if music_clip
                else audio_clip
            )

            # Add a slow, centered zoom so the still image has gentle motion.
            image_clip = ImageClip(numpy.array(background)).with_duration(duration)

            def zoom_frame(get_frame, time):
                frame = get_frame(time)
                scale = 1.0 + 0.08 * min(time / max(duration, 0.001), 1.0)
                zoomed_width = int(target_width * scale)
                zoomed_height = int(target_height * scale)
                zoomed = Image.fromarray(frame).resize(
                    (zoomed_width, zoomed_height), Image.Resampling.LANCZOS
                )
                left = (zoomed_width - target_width) // 2
                top = (zoomed_height - target_height) // 2
                return numpy.array(
                    zoomed.crop(
                        (left, top, left + target_width, top + target_height)
                    )
                )

            image_clip = image_clip.transform(zoom_frame)
            video = image_clip.with_audio(final_audio)
            
            # Write to file with Instagram-compatible settings (30 fps, H.264 + AAC)
            video.write_videofile(
                temp_video_path,
                codec='libx264',
                audio_codec='aac',
                audio_fps=44100,
                audio_bitrate='128k',
                fps=30,
                bitrate='4000k',
                preset='medium',
                ffmpeg_params=[
                    '-pix_fmt', 'yuv420p',
                    '-ar', '44100',
                    '-ac', '2',
                    '-movflags', '+faststart',
                ]
            )
            
            audio_clip.close()
            if music_clip:
                music_clip.close()
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
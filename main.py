from datetime import datetime
from gemini_processing import GeminiProcessing
from apod_api_helper import ApodApiHelper
from instagram_api_helper import InstagramApiHelper
from reel_generator import ReelGenerator
from io import BytesIO
import requests
import os

def work():
    print('\n' + "Working" + '\n')
    print("Current time: " + datetime.now().strftime("%H:%M:%S") + "\n")

    apod_helper = ApodApiHelper()
    apod_data = apod_helper.get_apod_data()

    if not apod_data:
        raise Exception("Failed to fetch APOD data from NASA.")

    if "error" in apod_data:
        raise Exception(f"Error: {apod_data.get('error', {}).get('message', 'Unknown error')}")

    # Extract APOD data
    title = apod_data["title"]
    image_by = apod_data.get('copyright')
    date_str = apod_data["date"]
    
    posted_dates_file = "posted_dates.txt"
    if os.path.exists(posted_dates_file):
        with open(posted_dates_file, "r") as f:
            if date_str in f.read():
                print(f"APOD for {date_str} has already been posted. Exiting.")
                return

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    date = date_obj.strftime("%m/%d/%Y")
    explanation = apod_data["explanation"]
    
    media_type = apod_data.get("media_type")
    if media_type == "video":
        image_hd_url = apod_data.get("thumbnail_url", apod_data.get("url"))
        image_url = apod_data.get("thumbnail_url", apod_data.get("url"))
    else:
        image_hd_url = apod_data.get("hdurl", apod_data.get("url"))
        image_url = apod_data.get("url")
    
    print("Data received from NASA. Processing data...")
    
    # Generate AI description for TTS voiceover narration
    bot = GeminiProcessing()
    bot_says = bot.generate_content(explanation, image_url)

    # Format Instagram caption using the raw NASA APOD explanation
    instagram_helper = InstagramApiHelper()
    caption = instagram_helper.write_caption(title, image_by, date, explanation)
    
    # Create and post the reel first; the image is the fallback if reel posting fails.
    print("Creating reel from APOD content...")
    reel_generator = ReelGenerator()
    
    # Prepare Gemini response for TTS narration (clean URLs/hashtags, sentence boundary trim)
    tts_text = reel_generator.prepare_tts_text(bot_says)
    
    try:
        video_path = reel_generator.create_reel(image_url, tts_text)
        
        # Upload video file to Instagram with raw APOD caption
        reel_result = instagram_helper.post_reel(
            video_path=video_path,
            caption=caption
        )
        print("\n" + reel_result + "\n")

        reel_succeeded = reel_result.startswith((
            "Reel published successfully",
            "Reel already published",
        ))
        if not reel_succeeded:
            raise RuntimeError(f"Reel posting failed: {reel_result}")
        
        # Clean up temporary file
        if os.path.exists(video_path):
            os.remove(video_path)
            
    except Exception as e:
        print(f"Error creating/posting reel: {str(e)}")
        # Ensure cleanup of temporary file in case of error
        if 'video_path' in locals() and os.path.exists(video_path):
            os.remove(video_path)
        print("Posting the APOD image as a fallback...")
        try:
            media_id = instagram_helper.create_media_id(image_hd_url, image_url, caption)
            result = instagram_helper.publish_media(media_id, caption)
        except Exception as image_error:
            print(f"Primary image fallback failed: {image_error}")
            result = instagram_helper.post_default_image(caption)
        print("\n" + result + "\n")
        
    # Record successful post
    with open(posted_dates_file, "a") as f:
        f.write(date_str + "\n")
    print("Idempotency recorded. Done.")

def reel_test():
    print('\n' + "Working" + '\n')
    print("Current time: " + datetime.now().strftime("%H:%M:%S") + "\n")

    reel_generator = ReelGenerator()
    image_url = "https://apod.nasa.gov/apod/image/2502/SaturnIR_CassiniKakitsev_960.jpg"
    description = """This infrared mosaic from the Cassini spacecraft shows Saturn's northern hemisphere in a light that is not visible to human eyes. The image was taken in 2006 and shows the gas giant's rings, as well as the hexagonal storm at its north pole. The storm is a persistent feature of the planet's atmosphere and has been observed for decades. The image was created using data from Cassini's visual and infrared mapping spectrometer, which can detect light at wavelengths beyond the visible spectrum. The false-color image was created by assigning visible colors to the infrared data, with red representing low clouds and green representing high clouds. The hexagonal storm is visible as a dark spot at the planet's north pole."""
    try:
        video_path = reel_generator.create_reel(image_url, description)
        
        # Upload video file to Instagram
        instagram_helper = InstagramApiHelper()
        reel_result = instagram_helper.post_reel(
            video_path=video_path,
            caption=f"\n\n{description}"
        )
        print("\n" + reel_result + "\n")
        
        # Clean up temporary file
        if os.path.exists(video_path):
            os.remove(video_path)
            
    except Exception as e:
        print(f"Error creating/posting reel: {str(e)}")
        # Ensure cleanup of temporary file in case of error
        if 'video_path' in locals() and os.path.exists(video_path):
            os.remove(video_path)

if __name__ == "__main__":
    work()
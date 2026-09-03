from datetime import datetime
from gemini_processing import GeminiProcessing
from apod_api_helper import ApodApiHelper
from instagram_api_helper import InstagramApiHelper
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
    
    # Generate AI description
    bot = GeminiProcessing()
    bot_says = bot.generate_content(explanation, image_url)

    # Create Instagram post
    instagram_helper = InstagramApiHelper()
    caption = instagram_helper.write_caption(title, image_by, date, bot_says)
    
    # First post the image
    try:
        media_id = instagram_helper.create_media_id(image_hd_url, image_url, caption)
        result = instagram_helper.publish_media(media_id, caption)
        print("\n" + result + "\n")
    except Exception as e:
        print(f"Failed to post image, attempting fallback. Error: {str(e)}")
        result = instagram_helper.post_default_image(caption)
        print("\n" + result + "\n")
""" 
    # Then create and post the reel
    print("Creating reel from APOD content...")
    reel_generator = ReelGenerator()
    
    # Use a shortened version of the bot's response for the audio
    short_description = bot_says[:500] if len(bot_says) > 500 else bot_says
    
    try:
        video_path = reel_generator.create_reel(image_url, short_description)
        
        # Upload video file to Instagram
        reel_result = instagram_helper.post_reel(
            video_path=video_path,
            caption=f"{title}\n\n{short_description}\n\nCredits: {image_by if image_by else 'NASA'}\n{date}"
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
        raise e
        
    # Record successful post
    with open(posted_dates_file, "a") as f:
        f.write(date_str + "\n")
    print("Idempotency recorded. Done.") """

""" def reel_test():
    print('\n' + "Working" + '\n')
    print("Current time: " + datetime.now().strftime("%H:%M:%S") + "\n")

    reel_generator = ReelGenerator()
    image_url = "https://apod.nasa.gov/apod/image/2502/SaturnIR_CassiniKakitsev_960.jpg"
    description = This infrared mosaic from the Cassini spacecraft shows Saturn's northern hemisphere in a light that is not visible to human eyes. The image was taken in 2006 and shows the gas giant's rings, as well as the hexagonal storm at its north pole. The storm is a persistent feature of the planet's atmosphere and has been observed for decades. The image was created using data from Cassini's visual and infrared mapping spectrometer, which can detect light at wavelengths beyond the visible spectrum. The false-color image was created by assigning visible colors to the infrared data, with red representing low clouds and green representing high clouds. The hexagonal storm is visible as a dark spot at the planet's north pole.
    try:
        video_path = reel_generator.create_reel(image_url, description)
        
        # Upload video file to Instagram - changed video_url to video_path
        instagram_helper = InstagramApiHelper()
        reel_result = instagram_helper.post_reel(
            video_path=video_path,  # Changed from video_url to video_path
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

    
# For testing purpose
if __name__ == "__main__":
    reel_test()

 """

work()
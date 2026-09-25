from datetime import datetime
from gemini_processing import GeminiProcessing
from apod_api_helper import ApodApiHelper
from instagram_api_helper import InstagramApiHelper
from reel_generator import ReelGenerator
from io import BytesIO
import requests
import os
import logging

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

def work():
    logger.info(
        "RUN SOURCE: %s",
        os.getenv("GITHUB_SHA", "local-working-tree"),
    )
    print('\n' + "Working" + '\n')
    print("Current time: " + datetime.now().strftime("%H:%M:%S") + "\n")

    apod_helper = ApodApiHelper()
    apod_data = apod_helper.get_apod_data()

    if not apod_data:
        raise Exception("Failed to fetch APOD data from NASA.")

    if "error" in apod_data:
        raise Exception(f"Error: {apod_data.get('error', {}).get('message', 'Unknown error')}")

    original_apod = apod_data

    # Do not repost an APOD date that has already succeeded.
    date_str = original_apod["date"]
    
    posted_dates_file = "posted_dates.txt"
    if os.path.exists(posted_dates_file):
        with open(posted_dates_file, "r") as f:
            if date_str in f.read():
                print(f"APOD for {date_str} has already been posted. Exiting.")
                return

    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    date = date_obj.strftime("%m/%d/%Y")
    test_video_path = os.getenv("TEST_VIDEO_PATH")
    instagram_helper = InstagramApiHelper()
    reel_generator = ReelGenerator()

    def post_candidate(candidate, direct_video=False):
        title = candidate["title"]
        image_by = candidate.get("copyright")
        explanation = candidate["explanation"]
        candidate_date = datetime.strptime(candidate["date"], "%Y-%m-%d").strftime("%m/%d/%Y")
        image_url = candidate.get("url")

        if test_video_path:
            bot_says = ""
        else:
            bot = GeminiProcessing()
            bot_says = bot.generate_content(explanation, None if direct_video else image_url)

        caption_explanation = bot_says if direct_video and bot_says else explanation
        caption = instagram_helper.write_caption(
            title, image_by, candidate_date, caption_explanation
        )
        hashtags = GeminiProcessing.extract_hashtags(bot_says)
        if hashtags:
            caption = f"{caption}\n\n{hashtags}"[:2200]

        if direct_video:
            video_path = candidate["url"]
        elif test_video_path:
            video_path = test_video_path
        else:
            tts_text = reel_generator.prepare_tts_text(bot_says)
            video_path = reel_generator.create_reel(image_url, tts_text)

        logger.info("REEL: posting candidate %s", video_path)
        result = instagram_helper.post_reel(video_path=video_path, caption=caption)
        if result.startswith("Reel processing pending"):
            raise TimeoutError(result)
        succeeded = result.startswith((
            "Reel published successfully",
            "Reel already published",
        ))
        if not succeeded:
            raise RuntimeError(f"Reel posting failed: {result}")
        return candidate, caption, video_path, result

    print("Data received from NASA. Processing data...")
    candidate = original_apod
    direct_video = candidate.get("media_type") == "video" and not test_video_path
    if direct_video:
        logger.info("APOD is a video; attempting to post NASA video directly")
    else:
        candidate = apod_helper.get_random_apod_data()
        logger.info("APOD is not a direct-postable video; using a random image APOD")

    video_path = None
    try:
        candidate, caption, video_path, reel_result = post_candidate(candidate, direct_video)
        print("\n" + reel_result + "\n")
        if video_path and not direct_video and not test_video_path and os.path.exists(video_path):
            os.remove(video_path)
    except TimeoutError as pending_error:
        logger.error("REEL PENDING: %s", pending_error)
        logger.info("REEL PENDING: leaving APOD unrecorded for the next scheduled retry")
        return
    except Exception as first_error:
        logger.exception("REEL CANDIDATE FAILED: %s", first_error)
        if direct_video:
            logger.info("DIRECT VIDEO FAILED: selecting a random image APOD")
            candidate = apod_helper.get_random_apod_data()
            video_path = None
            try:
                candidate, caption, video_path, reel_result = post_candidate(candidate)
                print("\n" + reel_result + "\n")
                if video_path and not test_video_path and os.path.exists(video_path):
                    os.remove(video_path)
            except TimeoutError as pending_error:
                logger.error("REEL PENDING: %s", pending_error)
                logger.info("REEL PENDING: leaving APOD unrecorded for the next scheduled retry")
                return
            except Exception as random_error:
                logger.exception("RANDOM APOD REEL FAILED: %s", random_error)
                fallback_caption = instagram_helper.write_caption(
                    candidate["title"],
                    candidate.get("copyright"),
                    datetime.strptime(candidate["date"], "%Y-%m-%d").strftime("%m/%d/%Y"),
                    candidate["explanation"],
                )
                try:
                    media_id = instagram_helper.create_media_id(
                        candidate.get("hdurl", candidate.get("url")),
                        candidate.get("url"),
                        fallback_caption,
                    )
                    instagram_helper.publish_media(media_id, fallback_caption)
                except Exception as image_error:
                    logger.exception("RANDOM APOD IMAGE FALLBACK FAILED: %s", image_error)
                    instagram_helper.post_default_image(fallback_caption)
        else:
            logger.info("REEL FAILED: posting the selected APOD image fallback")
            fallback_caption = instagram_helper.write_caption(
                candidate["title"],
                candidate.get("copyright"),
                datetime.strptime(candidate["date"], "%Y-%m-%d").strftime("%m/%d/%Y"),
                candidate["explanation"],
            )
            try:
                image_url = candidate.get("url")
                media_id = instagram_helper.create_media_id(
                    candidate.get("hdurl", image_url), image_url, fallback_caption
                )
                instagram_helper.publish_media(media_id, fallback_caption)
            except Exception as image_error:
                logger.exception("IMAGE FALLBACK FAILED: %s", image_error)
                instagram_helper.post_default_image(fallback_caption)

    # Record the date after either a confirmed reel or image fallback succeeds.
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
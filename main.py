import schedule
from datetime import time, timedelta, datetime

from config import nasa_api_key, instagram_id, instagram_access_token
from apod_api_helper import ApodApiHelper
from instagram_api_helper import InstagramApiHelper

def post_apod():
    print( '\n' + "Working" +"\n")

    apod_helper = ApodApiHelper()
    apod_data = apod_helper.get_apod_data()

    #Extract the date from the APOD data
    title = apod_data["title"]
    image_by = apod_data["copyright"]
    date = apod_data["date"]
    explanation = apod_data["explanation"]
    image_url = apod_data["hdurl"]

    # Create an instance of the InstagramApiHelper class to post the image
    post_APOD = InstagramApiHelper()
    media_id = post_APOD.create_media_id(title, image_by, date, explanation, image_url, "APOD")
    result = post_APOD.publish_media(media_id)
    print(result)


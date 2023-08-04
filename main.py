import time
import schedule
from datetime import datetime
from apod_api_helper import ApodApiHelper
from instagram_api_helper import InstagramApiHelper

def work():
    print( '\n' + "Working" + "\n")
    print("Current time: " + datetime.now().strftime("%H:%M:%S") + "\n")

    
    apod_helper = ApodApiHelper()
    apod_data = apod_helper.get_apod_data()

    # Check if the response contains an error message
    if "error" in apod_data:
        print(f"Error: {apod_data['error']['message']}")
    else:
        # Extract the date from the APOD data
        title = apod_data["title"]
        image_by = apod_data.get('copyright')
        if image_by is None:
            image_by = "Research Team"
       

        # Extract the date from the APOD data and format it as "MM/DD/YYYY"
        date_str = apod_data["date"]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        date = date_obj.strftime("%m/%d/%Y")
        explanation = apod_data["explanation"]
        image_url = apod_data["hdurl"]
        



        # Create an instance of the InstagramApiHelper class to post the image
        post_APOD = InstagramApiHelper()
        caption = post_APOD.write_caption(title, image_by, date, explanation, "APOD")
        media_id = post_APOD.create_media_id(image_url, caption)
        result = post_APOD.publish_media(media_id, caption)           
        print("\n" + result + "\n")


for i in range(5):
    work()
    time.sleep(120)
    
# schedule.every().day.at("14:00:00").do(work)

# while True:
#     schedule.run_pending()
#     time.sleep(1)


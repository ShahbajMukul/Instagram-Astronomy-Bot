
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

instagram_id = os.getenv("INSTAGRAM_ID")
instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

class InstagramApiHelper:
    def __init__(self):
        load_dotenv()
        self.instagram_id = os.getenv("INSTAGRAM_ID")
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    def write_caption(self, title, image_by, date, explanation):

        if len(title) > 30:
            if image_by:
                caption = f"\n{title}\n\n{explanation}\n\nImage Credit: {image_by}\n{date}"
            else:
                caption = f"\n{title}\n\n{explanation}\n\n{date}"
        else:
            if image_by:
                caption = f"{title}\n\n{explanation}\n\nImage Credit: {image_by}\n{date}"
            else:
                caption = f"{title}\n\n{explanation}\n\n{date}"
        return caption


    def create_media_id(self, image_hd_url, image_url, caption):
        url = f"https://graph.facebook.com/v21.0/{instagram_id}/media?image_url={image_hd_url}&access_token={instagram_access_token}&caption={caption}"
        response = requests.post(url)
        data = json.loads(response.text)
        if "id" in data:
            print("Media ID created for instagram. Trying to post...")
            return data["id"]
        elif response.status_code == 400:
            url=f"https://graph.facebook.com/v21.0/{instagram_id}/media?image_url={image_url}&access_token={instagram_access_token}&caption={caption}"
            response = requests.post(url)
            data = json.loads(response.text)
            return "hd_image failed, attempted regular image to be posted"
        elif "error" in data:
            print("Error from create_media_id: " + data["error"]["message"] + "\n")
            return "Something went wrong. Check the Error:" + data["error"]["message"] + "\n"
        else:
            return "Limit reached"
        

    def publish_media(self, media_id, caption):
        url = f"https://graph.facebook.com/v21.0/{instagram_id}/media_publish?access_token={instagram_access_token}&creation_id={media_id}"
        response = requests.post(url)

        if response.status_code == 200:
            return "Image posted successfully!"
        elif response.status_code == 400:
            return self.post_default_image(caption)
        else:
            return f"Something went wrong while posting the image! Status code: {response.status_code}. Response: {response.text}"

    def post_default_image(self, caption):
        print("\nPosting default image... \n")
        default_image_url = "https://www.nasa.gov/sites/default/files/styles/side_image/public/thumbnails/image/apod_logo.png?itok=6It-nhCr"
        caption += "\nToday's APOD is not supported by Instagram 😞"
        post_id = self.create_media_id(default_image_url, default_image_url, caption)
        url = f"https://graph.facebook.com/v19.0/{instagram_id}/media_publish?access_token={instagram_access_token}&creation_id={post_id}"
        response = requests.post(url)
        if response.status_code == 200:
            return "Image posted successfully!"
        else:
            return f"Something went wrong while posting the image! Status code: {response.status_code}. Response: {response.text}"
    

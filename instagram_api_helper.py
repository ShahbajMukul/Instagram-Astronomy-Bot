import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

instagram_id = os.getenv("INSTAGRAM_ID")
instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

class InstagramApiHelper:

    def write_caption(self, title, image_by, date, explanation, source):
        explanation = self.generate_emoji(explanation)

        #formatting the caption to fit the Instagram title
        if len(title) > 30: 
            caption = f"\n{title}\n\n{explanation}\n\n©:{image_by}\n{date}"
        else:
            caption = f"{title}\n\n{explanation}\n\n©:{image_by}\n{date}" 

        final_caption = self.generate_hashtags(source, caption)

        return final_caption


    def create_media_id(self, image_url, caption):
        url = f"https://graph.facebook.com/v17.0/{instagram_id}/media?image_url={image_url}&access_token={instagram_access_token}&caption={caption}"
        response = requests.post(url)
        data = json.loads(response.text)
        if "id" in data:
            return data["id"]
        elif "error" in data:
            print("Error from create_media_id: " + data["error"]["message"] + "\n")
            return "Something went wrong. Check the Error:" + data["error"]["message"] + "\n"
        else:
            return "Limit reached"
        

    def publish_media(self, media_id, caption):
        url = f"https://graph.facebook.com/v17.0/{instagram_id}/media_publish?access_token={instagram_access_token}&creation_id={media_id}"
        response = requests.post(url)

        if response.status_code == 200:
            return "Image posted successfully!"
        elif response.status_code == 400:
            return self.post_default_image(caption)
        else:
            return "Something went wrong while posting the image!"

    def post_default_image(self, caption):
        print("\nPosting default image... \n")
        default_image_url = "https://www.nasa.gov/sites/default/files/styles/side_image/public/thumbnails/image/apod_logo.png?itok=6It-nhCr"
        caption += "\nToday's APOD is not supported by Instagram 😞"
        post_id = self.create_media_id(default_image_url, caption)
        url = f"https://graph.facebook.com/v17.0/{instagram_id}/media_publish?access_token={instagram_access_token}&creation_id={post_id}"
        response = requests.post(url)
        if response.status_code == 200:
            return "Image posted successfully!"
        else:
            return "Something went wrong while posting the image!"
    

    def generate_emoji(self, caption):
        if not isinstance(caption, str):
            return caption
        found = True # we assume that we will find at least one emoji if there is a word match.
        emoji_list = [
                    ["🌟", "star", "stars"],
                    ["🚀", "rocket", "rockets"],
                    ["🌌", "galaxy", "galaxies"],
                    ["🌠", "shooting star", "shooting stars"],
                    ["🔭", "telescope", "telescopes"],
                    ["🛰️", "satellite", "satellites"],
                    ["🌛", "moon", "moons"],
                    ["☀️", "sun", "suns"],
                    ["🌎", "earth", "earths"],
                    ["👽", "alien", "aliens"],
                    ["👨‍🚀", "astronaut", "astronauts"],
                    ["💥", "explosion", "explosions"]
                    ]
        for emoji, singular, plural in emoji_list:
            if singular in caption or plural in caption:
                if found:  # we add just a new line if we find at least one emoji
                    caption += "\n"
                    found = False
                caption += emoji  # we add the emoji to the explanation
        return caption        

    def generate_hashtags(self, source, caption):
        if source == "APOD":
            caption += "\n\n%23NASA %23APOD %23Astronomy %23Space %23Science"
        #More to be added later
        return caption 




    def get_user_post(self, user):
        media_url = f"https://graph.facebook.com/v17.0/{user}/media?access_token={instagram_access_token}"
        media_response = requests.get(media_url)
        media_data = media_response.json()
        if "data" in media_data and len(media_data["data"]) > 0:
            return media_data["data"][0]
        else:
            return None
'''
    # Make a function that will comment on latest NASA posts
    def comment_on_nasa_post(self):
        nasa_user_id = 528817151
        my_comment = "yay! My first comment!!"

        media_url = f"https://graph.facebook.com/v17.0/{nasa_user_id}/media?access_token={instagram_access_token}"
        media_response = requests.get(media_url)
        media_data = media_response.json()
        new_post_id = media_data["data"][0]["id"]

        comment_url = f"https://graph.facebook.com/v17.0/{new_post_id}/comments?message={my_comment}&access_token={instagram_access_token}"
        comment_response = requests.post(comment_url)
        comment_data = comment_response.json()
        comment_id = comment_data["id"]

        print(f"Commented with ID: {comment_id}")


    def get_user_ig_id(self, user):
        user_url = f"https://graph.facebook.com/v17.0/{user}?access_token={instagram_access_token}"
        user_response = requests.get(user_url)
        user_data = user_response.json()
        user_id = user_data["id"]
        return user_id
'''

'''
#Tried to use this to format the image, but it didn't work. Time constraints.
def format_image(image_url):
    # Use requests to download the image from the URL
    response = requests.get(image_url)

    # Use BytesIO to create a file-like object from the response content
    image_data = BytesIO(response.content)

    # Use Image.open to open the image from the file-like object
    image = Image.open(image_data)

    org_width, org_height = image.size

    aspect_ratio = org_width / org_height

    if org_width > org_height:
        new_width = 1080
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = 1080
        new_width = int(new_height * aspect_ratio)

    resized_image = image.resize((new_width, new_height))

    final_image = Image.new("RGB", (1080, 1080), (0, 0, 0))
    x_offset = int((1080 - new_width) // 2)
    y_offset = int((1080 - new_height) // 2)
    final_image.paste(resized_image, (x_offset, y_offset))

    # Convert the final_image to bytes
    image_bytes = final_image.tobytes()

    return image_bytes
'''

        
        
        

        
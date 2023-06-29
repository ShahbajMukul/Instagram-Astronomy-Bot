import requests
import json
import random
from config import instagram_id, instagram_access_token

class InstagramApiHelper:


    def create_media_id(self, title, image_by, date, explanation, image_url, source):
        explanation = self.generate_emoji(explanation)

        caption = f"{source}\n\n{title}\n\n{explanation}\n\n©:{image_by}\n{date}"
        final_caption = self.generate_hashtags(source, caption)
        url = f"https://graph.facebook.com/v17.0/{instagram_id}/media?image_url={image_url}&access_token={instagram_access_token}&caption={final_caption}"
        response = requests.post(url)
        data = json.loads(response.text)
        return data["id"]
    





    '''def create_media_id(self, title, image_by, date, explanation, image_url, source):
        caption = f"{source}\n\n{title}\n©:{image_by}\n\n{date}\n\n{explanation}"
        caption = self.generate_emoji(caption)
        final_caption = self.generate_hashtags(source, caption)
        url = f"https://graph.facebook.com/v17.0/{instagram_id}/media?image_url={image_url}&access_token={instagram_access_token}&caption={final_caption}"
        response = requests.post(url)
        data = json.loads(response.text)
        return data["id"]'''
    
    def publish_media(self, media_id):
        url = f"https://graph.facebook.com/v17.0/{instagram_id}/media_publish?access_token={instagram_access_token}&creation_id={media_id}"
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


        
        
        

        
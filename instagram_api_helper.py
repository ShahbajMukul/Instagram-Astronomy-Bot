import os
import requests
import json
import random

instagram_id = os.getenv("INSTAGRAM_ID")
instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

class InstagramApiHelper:
    def create_media_id(self, title, image_by, date, explanation, image_url, source):
        caption = f"{source}\n{title}\n\n©:{image_by}\n{date}\n\n{explanation}"
        caption = self.generate_emoji(caption)
        caption = self.generate_hashtags(source, caption)
        url = f"https://graph.facebook.com/v17.0/{instagram_id}/media?image_url={image_url}&access_token={instagram_access_token}&caption={caption}"
        response = requests.post(url)
        data = json.loads(response.text)
        return data["id"]
    
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
        emoji_list = [["🌟", "star"],
                  ["🚀", "rocket"],
                  ["🌌", "milky way"],
                  ["🌠", "shooting star"],
                  ["🔭", "telescope"],
                  ["🛰️", "satellite"],
                  ["🌛", "moon"],
                  ["☀️", "sun"]]
        for emoji, word in emoji_list:
            if word in caption:
                if found: # we add just a new line if we find at least one emoji
                    caption += "\n"
                    found = False   
            caption += emoji # we add the emoji to the explanation 
        return caption        
    
    def generate_hashtags(self, source, caption):
        if source == "APOD":
            caption += "\n#NASA #APOD #Astronomy #Space #Science"
        #More to be added later
        return caption


        
        
        

        
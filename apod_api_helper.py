import requests
import json
import os

from dotenv import load_dotenv
load_dotenv()

nasa_api_key = os.getenv("NASA_API_KEY")

class ApodApiHelper:
    def get_apod_data(self):
       url = f"https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}"
       response = requests.get(url)
       data = json.loads(response.text)
       try:
           data["copyright"] = data["copyright"].replace("\n", ",").lstrip()
       except KeyError:
           pass

       return data 

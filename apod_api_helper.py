import os
import requests
import json
import datetime

nasa_api_key = os.getenv("NASA_API_KEY")

class ApodApiHelper:
    def get_apod_data(self):
       url = f"https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}"
       response = requests.get(url)
       data = json.loads(response.text)
       return data 

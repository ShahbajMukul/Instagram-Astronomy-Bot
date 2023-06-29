import requests
import json
from config import nasa_api_key
import datetime

class ApodApiHelper:
    def get_apod_data(self):
       url = f"https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}"
       response = requests.get(url)
       data = json.loads(response.text)
       return data 

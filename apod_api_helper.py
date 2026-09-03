import requests
import os

from dotenv import load_dotenv
load_dotenv()

nasa_api_key = os.getenv("NASA_API_KEY")


class ApodApiHelper:
    def get_apod_data(self):
        print("Fetching data from NASA APOD API...")
        url = f"https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}&thumbs=True"
        try:
            response = requests.get(url, timeout=10)  # Add a timeout of 10 seconds
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            data["copyright"] = data.get("copyright", "")
            data["copyright"] = data["copyright"].replace("\n", ",").lstrip()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from NASA APOD API: {e}")
            return None  

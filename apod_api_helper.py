import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()


class ApodApiHelper:
    def __init__(self):
        load_dotenv()

    def get_apod_data(self, max_attempts: int = 3, timeout: int = 30):
        print("Fetching data from NASA APOD API...")
        api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
        url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&thumbs=True"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "Instagram-Astronomy-Bot/1.0"
            )
        }

        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                data["copyright"] = data.get("copyright", "")
                data["copyright"] = data["copyright"].replace("\n", ",").lstrip()
                return data
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt}/{max_attempts} failed to fetch APOD data: {e}")
                if attempt < max_attempts:
                    time.sleep(2)
                else:
                    print("All attempts to fetch APOD data failed.")
                    return None  

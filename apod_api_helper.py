import os
import time
import random
import requests
from datetime import date, timedelta
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

    def get_random_apod_data(self, timeout: int = 30):
        """Fetch the APOD for one randomly selected date."""
        api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
        first_apod_date = date(2015, 11, 30) # The first date for which APOD data is available
        days_since_first_apod = (date.today() - first_apod_date).days
        random_date = first_apod_date + timedelta(
            days=random.randint(0, days_since_first_apod)
        )
        date_string = random_date.isoformat()
        url = (
            "https://api.nasa.gov/planetary/apod?"
            f"start_date={date_string}&end_date={date_string}&api_key={api_key}"
        )

        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        # include in the explanation that this is a random APOD because the original APOD was a video
        # fix the error : TypeError: list indices must be integers or slices, not str
        if isinstance(data, list):
            data = data[0]  
        data["explanation"] = f"`This is a random APOD because the today's original APOD was a video and we couldn't use it` {data['explanation']}"
        data["copyright"] = data.get("copyright", "").replace("\n", ",").lstrip()
        return data

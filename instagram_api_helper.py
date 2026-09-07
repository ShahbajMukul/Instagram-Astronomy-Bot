import requests
import json
import os
from dotenv import load_dotenv
from io import BytesIO  
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
        if len(caption) > 2200:
            caption = caption[:2197] + "..."
        return caption

    def create_media_id(self, image_hd_url, image_url, caption):
        url = f"https://graph.facebook.com/v26.0/{self.instagram_id}/media"
        params = {
            "image_url": image_hd_url,
            "access_token": self.access_token,
            "caption": caption
        }
        response = requests.post(url, params=params)
        data = response.json()
        if "id" in data:
            print("Media ID created for instagram. Waiting for container to be ready...")
            return data["id"]
        elif response.status_code == 400:
            print("HD image failed, attempting regular image...")
            params["image_url"] = image_url
            response = requests.post(url, params=params)
            data = response.json()
            if "id" in data:
                return data["id"]
            else:
                raise Exception(f"Failed to create media id with regular image: {data.get('error', {}).get('message')}")
        else:
            raise Exception(f"Failed to create media id: {data.get('error', {}).get('message', 'Unknown error')}")
        

    def publish_media(self, media_id, caption):
        # Wait for the container to be ready
        import time
        attempts = 0
        max_attempts = 12
        while attempts < max_attempts:
            status = self.check_container_status(media_id)
            if status == "FINISHED" or status == "PUBLISHED" or status == "ERROR":
                break
            elif status == "IN_PROGRESS":
                print("Image container is still processing...")
            attempts += 1
            time.sleep(10)
            
        url = f"https://graph.facebook.com/v26.0/{self.instagram_id}/media_publish"
        params = {
            "access_token": self.access_token,
            "creation_id": media_id
        }
        response = requests.post(url, params=params)

        if response.status_code == 200:
            return "Image posted successfully!"
        else:
            raise Exception(f"Something went wrong while posting the image! Status code: {response.status_code}. Response: {response.text}")
    def post_default_image(self, caption):
        print("\nPosting default image... \n")
        default_image_url = "https://www.nasa.gov/sites/default/files/styles/side_image/public/thumbnails/image/apod_logo.png?itok=6It-nhCr"
        caption += "\nToday's APOD is not supported by Instagram 😞"
        post_id = self.create_media_id(default_image_url, default_image_url, caption)
        return self.publish_media(post_id, caption)

    def create_reel_container(self, video_path, caption, thumbnail_url=None):
        """Create a container for a reel upload using Instagram Graph API"""
        url = f"https://graph.facebook.com/v26.0/{self.instagram_id}/media"
        
        try:
            # Check if video_path is a remote URL or local file path
            if video_path.startswith("http://") or video_path.startswith("https://"):
                params = {
                    "access_token": self.access_token,
                    "caption": caption,
                    "media_type": "REELS",
                    "video_url": video_path,
                }
                if thumbnail_url:
                    params["thumbnail_url"] = thumbnail_url
                
                response = requests.post(url, params=params)
                data = response.json()
                if "id" not in data:
                    print(f"Error creating reel container: {data.get('error', {}).get('message', 'Unknown error')}")
                    return None
                return data["id"]

            else:
                # Resumable upload for local video file
                file_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
                params = {
                    "access_token": self.access_token,
                    "caption": caption,
                    "media_type": "REELS",
                    "upload_type": "resumable",
                }
                if thumbnail_url:
                    params["thumbnail_url"] = thumbnail_url

                response = requests.post(url, params=params)
                data = response.json()

                if "id" not in data:
                    print(f"Error initializing reel container: {data.get('error', {}).get('message', 'Unknown error')}")
                    return None

                container_id = data["id"]
                upload_uri = data.get("uri")

                if upload_uri:
                    upload_headers = {
                        "Authorization": f"OAuth {self.access_token}",
                        "offset": "0",
                        "file_size": str(file_size),
                        "Content-Length": str(file_size),
                        "Content-Type": "application/octet-stream",
                    }
                    if os.path.exists(video_path):
                        with open(video_path, "rb") as video_file:
                            upload_response = requests.post(upload_uri, headers=upload_headers, data=video_file)
                        upload_data = upload_response.json()
                        if upload_response.status_code != 200 or not upload_data.get("success", True):
                            print(
                                "Error uploading video content: "
                                f"HTTP {upload_response.status_code} "
                                f"{upload_response.text}"
                            )
                            return None

                return container_id

        except Exception as e:
            print(f"Error uploading video file: {str(e)}")
            return None

    def check_container_status(self, container_id):
        """Check the status of a media container"""
        url = f"https://graph.facebook.com/v26.0/{container_id}?fields=status_code,status&access_token={self.access_token}"
        response = requests.get(url)
        data = json.loads(response.text)
        
        if 'error' in data:
            print(f"Error checking reel status: {data['error']['message']}")
            return 'ERROR'
            
        status_code = data.get('status_code', '')
        status_message = data.get('status', '')
        print(f"Reel status: {status_code} - {status_message}")
        
        if 'Error:' in str(status_message):
            if '2207026' in str(status_message):
                print("Video format error: Please ensure the video meets Instagram requirements:")
                print("- Format: MP4 (preferred)")
                print("- Length: 3-90 seconds")
                print("- Size: Maximum 4GB")
                print("- Aspect ratio: 9:16 (portrait)")
                print("- Resolution: Minimum 720 pixels width")
                print("- Codec: H.264")
                print("- Frame rate: 30fps (recommended)")
            return 'ERROR'
        
        return status_code

    def publish_reel(self, container_id):
        """Publish a reel after it has been uploaded and processed"""
        url = f"https://graph.facebook.com/v26.0/{self.instagram_id}/media_publish"
        params = {
            'creation_id': container_id,
            'access_token': self.access_token
        }
        response = requests.post(url, params=params)
        data = json.loads(response.text)

        if "id" in data:
            return f"Reel published successfully! ID: {data['id']}"
        elif "error" in data:
            return f"Error publishing reel: {data['error']['message']}"
        return "Unknown error occurred while publishing reel"

    def post_reel(self, video_path, caption, thumbnail_url=None, max_attempts=2):
        """Complete process to post a reel including creation, status checking, and publishing"""
        print(f"Starting reel upload process from URL: {video_path}")
        container_id = self.create_reel_container(video_path, caption, thumbnail_url)
        if not container_id:
            return "Failed to create reel container"

        import time
        attempts = 0
        while attempts < max_attempts:
            print(f"Checking reel status (attempt {attempts + 1}/{max_attempts})")
            status = self.check_container_status(container_id)
            
            if status == "FINISHED" or status == "ERROR":
                print("Video processing completed successfully")
                return self.publish_reel(container_id)

            elif status == "IN_PROGRESS":
                print("Video is still processing...")
            elif status == "PUBLISHED":
                return "Reel already published"
            
            attempts += 1
            wait_time = 10  # Increased wait time between checks
            print(f"Waiting {wait_time} seconds before next status check...")
            time.sleep(wait_time)

        return "Timeout waiting for video processing. The video may still be processing in the background."


from instagram_api_helper import InstagramApiHelper


"""APOD

Fireworks vs Supermoon

On July 4, an almost Full Moon rose in planet Earth's evening skies. Also known as a Buck Moon, the full lunar phase (full on July 3 at 11:39 UTC) was near perigee, the closest point in the Moon's almost monthly orbit around planet Earth. That qualified this July's Full Moon as a supermoon, the first of four supermoons in 2023. Seen from Cocoa Beach along Florida's Space Coast on July 4, any big, bright, beautiful Full Moon would still have to compete for attention though. July's super-moonrise was captured here against a super-colorful fireworks display.
🌛

©:Michael Seeley
07/06/2023"""

sample_apod = {
    "title" : "Fireworks vs Supermoon",
    "image_by" : "Michael Seeley",
    "explanation": "On July 4, an almost Full Moon rose in planet Earth's evening skies. Also known as a Buck Moon, the full lunar phase (full on July 3 at 11:39 UTC) was near perigee, the closest point in the Moon's almost monthly orbit around planet Earth. That qualified this July's Full Moon as a supermoon, the first of four supermoons in 2023. Seen from Cocoa Beach along Florida's Space Coast on July 4, any big, bright, beautiful Full Moon would still have to compete for attention though. July's super-moonrise was captured here against a super-colorful fireworks display.",
    "date": "07/06/2023",
    "image_url": "https://apod.nasa.gov/apod/image/2307/CocoaBeach_BuckMoon_Seeley-201_1100.jpg",
    "source" : "APOD"
}
#create_media_id
# expected normal case
def test_create_media_id():
    insta = InstagramApiHelper()
    acutal_media_id = insta.create_media_id()

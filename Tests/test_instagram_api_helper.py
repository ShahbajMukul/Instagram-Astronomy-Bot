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
'''def test_create_media_id():
    insta = InstagramApiHelper()
    acutal_media_id = insta.create_media_id()
'''import unittest
from instagram_api_helper import InstagramApiHelper

class TestInstagramApiHelper(unittest.TestCase):

    def setUp(self):
        self.insta = InstagramApiHelper()

    def test_write_caption(self):
        title = "Fireworks vs Supermoon"
        image_by = "Michael Seeley"
        date = "07/06/2023"
        explanation = "On July 4, an almost Full Moon rose in planet Earth's evening skies. Also known as a Buck Moon, the full lunar phase (full on July 3 at 11:39 UTC) was near perigee, the closest point in the Moon's almost monthly orbit around planet Earth. That qualified this July's Full Moon as a supermoon, the first of four supermoons in 2023. Seen from Cocoa Beach along Florida's Space Coast on July 4, any big, bright, beautiful Full Moon would still have to compete for attention though. July's super-moonrise was captured here against a super-colorful fireworks display."
        source = "APOD"

        expected_caption = "Fireworks vs Supermoon\n\nOn July 4, an almost Full Moon rose in planet Earth's evening skies. Also known as a Buck Moon, the full lunar phase (full on July 3 at 11:39 UTC) was near perigee, the closest point in the Moon's almost monthly orbit around planet Earth. That qualified this July's Full Moon as a supermoon, the first of four supermoons in 2023. Seen from Cocoa Beach along Florida's Space Coast on July 4, any big, bright, beautiful Full Moon would still have to compete for attention though. July's super-moonrise was captured here against a super-colorful fireworks display.\n\n©:Michael Seeley\n07/06/2023\n\n%23NASA %23APOD %23Astronomy %23Space %23Science"

        actual_caption = self.insta.write_caption(title, image_by, date, explanation, source)

        self.assertEqual(actual_caption, expected_caption)

    def test_create_media_id(self):
        image_url = "https://apod.nasa.gov/apod/image/2307/CocoaBeach_BuckMoon_Seeley-201_1100.jpg"
        caption = "Fireworks vs Supermoon\n\nOn July 4, an almost Full Moon rose in planet Earth's evening skies. Also known as a Buck Moon, the full lunar phase (full on July 3 at 11:39 UTC) was near perigee, the closest point in the Moon's almost monthly orbit around planet Earth. That qualified this July's Full Moon as a supermoon, the first of four supermoons in 2023. Seen from Cocoa Beach along Florida's Space Coast on July 4, any big, bright, beautiful Full Moon would still have to compete for attention though. July's super-moonrise was captured here against a super-colorful fireworks display.\n\n©:Michael Seeley\n07/06/2023"

        media_id = self.insta.create_media_id(image_url, caption)

        self.assertIsNotNone(media_id)

    def test_publish_media(self):
        media_id = "123456789"
        caption = "Fireworks vs Supermoon\n\nOn July 4, an almost Full Moon rose in planet Earth's evening skies. Also known as a Buck Moon, the full lunar phase (full on July 3 at 11:39 UTC) was near perigee, the closest point in the Moon's almost monthly orbit around planet Earth. That qualified this July's Full Moon as a supermoon, the first of four supermoons in 2023. Seen from Cocoa Beach along Florida's Space Coast on July 4, any big, bright, beautiful Full Moon would still have to compete for attention though. July's super-moonrise was captured here against a super-colorful fireworks display.\n\n©:Michael Seeley\n07/06/2023"

        result = self.insta.publish_media(media_id, caption)

        self.assertEqual(result, "Image posted successfully!")

    def test_post_default_image(self):
        caption = "Fireworks vs Supermoon\n\nOn July 4, an almost Full Moon rose in planet Earth's evening skies. Also known as a Buck Moon, the full lunar phase (full on July 3 at 11:39 UTC) was near perigee, the closest point in the Moon's almost monthly orbit around planet Earth. That qualified this July's Full Moon as a supermoon, the first of four supermoons in 2023. Seen from Cocoa Beach along Florida's Space Coast on July 4, any big, bright, beautiful Full Moon would still have to compete for attention though. July's super-moonrise was captured here against a super-colorful fireworks display.\n\n©:Michael Seeley\n07/06/2023"

        result = self.insta.post_default_image(caption)

        self.assertEqual(result, "Image posted successfully!")

    def test_generate_emoji(self):
        caption = "Fireworks vs Supermoon\n\nOn July 4, an almost Full Moon rose in planet Earth's evening skies. Also known as a Buck Moon, the full lunar phase (full on July 3 at 11:39 UTC) was near perigee, the closest point in the Moon's almost monthly orbit around planet Earth. That qualified this July's Full Moon as a supermoon, the first of four supermoons in 2023. Seen from Cocoa Beach along Florida's Space Coast on July 4, any big, bright, beautiful Full Moon would still have to compete for attention though. July's super-moonrise was captured here against a super-colorful fireworks display.\n\n©:Michael Seeley\n07/06/2023"

        caption_with_emoji = self.insta.generate_emoji(caption)

        self.assertEqual(caption_with_emoji, caption)

    def test_generate_hashtags(self):
        source = "APOD"
        caption = "Fireworks vs Supermoon\n\nOn July 4, an almost Full Moon rose in planet Earth's evening skies. Also known as a Buck Moon, the full lunar phase (full on July 3 at 11:39 UTC) was near perigee, the closest point in the Moon's almost monthly orbit around planet Earth. That qualified this July's Full Moon as a supermoon, the first of four supermoons in 2023. Seen from Cocoa Beach along Florida's Space Coast on July 4, any big, bright, beautiful Full Moon would still have to compete for attention though. July's super-moonrise was captured here against a super-colorful fireworks display.\n\n©:Michael Seeley\n07/06/2023"

        caption_with_hashtags = self.insta.generate_hashtags(source, caption)

        self.assertEqual(caption_with_hashtags, "Fireworks vs Supermoon\n\nOn July 4, an almost Full Moon rose in planet Earth's evening skies. Also known as a Buck Moon, the full lunar phase (full on July 3 at 11:39 UTC) was near perigee, the closest point in the Moon's almost monthly orbit around planet Earth. That qualified this July's Full Moon as a supermoon, the first of four supermoons in 2023. Seen from Cocoa Beach along Florida's Space Coast on July 4, any big, bright, beautiful Full Moon would still have to compete for attention though. July's super-moonrise was captured here against a super-colorful fireworks display.\n\n©:Michael Seeley\n07/06/2023\n\n%23NASA %23APOD %23Astronomy %23Space %23Science")

if __name__ == '__main__':
    unittest.main()
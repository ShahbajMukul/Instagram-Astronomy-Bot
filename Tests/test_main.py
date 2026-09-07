import unittest
from unittest.mock import patch, MagicMock
import main

class TestMainWorkflow(unittest.TestCase):
    @patch('main.open', create=True)
    @patch('main.os.path.exists')
    @patch('main.ReelGenerator')
    @patch('main.InstagramApiHelper')
    @patch('main.GeminiProcessing')
    @patch('main.ApodApiHelper')
    def test_work_wires_raw_caption_and_gemini_tts(
        self,
        mock_apod_cls,
        mock_gemini_cls,
        mock_insta_cls,
        mock_reel_cls,
        mock_exists,
        mock_open
    ):
        mock_exists.return_value = False

        mock_apod_helper = MagicMock()
        mock_apod_cls.return_value = mock_apod_helper
        mock_apod_helper.get_apod_data.return_value = {
            "title": "Cosmic Mystery",
            "copyright": "NASA / Hubble",
            "date": "2026-09-05",
            "explanation": "Raw APOD explanation text from NASA.",
            "media_type": "image",
            "url": "https://example.com/image.jpg",
            "hdurl": "https://example.com/image_hd.jpg"
        }

        mock_gemini = MagicMock()
        mock_gemini_cls.return_value = mock_gemini
        mock_gemini.generate_content.return_value = "Gemini generated poetic narration."

        mock_insta = MagicMock()
        mock_insta_cls.return_value = mock_insta
        mock_insta.write_caption.return_value = "Formatted Raw APOD Caption"
        mock_insta.create_media_id.return_value = "media_123"
        mock_insta.publish_media.return_value = "Image posted successfully!"
        mock_insta.post_reel.return_value = "Reel published successfully! ID: reel_123"

        mock_reel_gen = MagicMock()
        mock_reel_cls.return_value = mock_reel_gen
        mock_reel_gen.prepare_tts_text.side_effect = lambda t: t
        mock_reel_gen.create_reel.return_value = "mock_video.mp4"

        # Run work()
        main.work()

        # Check caption used raw explanation, NOT Gemini output
        mock_insta.write_caption.assert_called_once_with(
            "Cosmic Mystery",
            "NASA / Hubble",
            "09/05/2026",
            "Raw APOD explanation text from NASA."
        )

        # Check reel creation used Gemini response for TTS
        mock_reel_gen.create_reel.assert_called_once_with(
            "https://example.com/image.jpg",
            "Gemini generated poetic narration."
        )

        mock_insta.post_reel.assert_called_once_with(
            video_path="mock_video.mp4",
            caption="Formatted Raw APOD Caption"
        )
        mock_insta.create_media_id.assert_not_called()

    @patch('main.open', create=True)
    @patch('main.os.path.exists')
    @patch('main.ReelGenerator')
    @patch('main.InstagramApiHelper')
    @patch('main.GeminiProcessing')
    @patch('main.ApodApiHelper')
    def test_work_falls_back_to_image_when_reel_fails(
        self,
        mock_apod_cls,
        mock_gemini_cls,
        mock_insta_cls,
        mock_reel_cls,
        mock_exists,
        mock_open
    ):
        mock_exists.return_value = False
        mock_apod_cls.return_value.get_apod_data.return_value = {
            "title": "Cosmic Mystery",
            "copyright": None,
            "date": "2026-09-05",
            "explanation": "Raw explanation.",
            "media_type": "image",
            "url": "https://example.com/image.jpg",
            "hdurl": "https://example.com/image_hd.jpg",
        }
        mock_gemini_cls.return_value.generate_content.return_value = "Narration."
        mock_insta = mock_insta_cls.return_value
        mock_insta.write_caption.return_value = "Caption"
        mock_insta.create_media_id.return_value = "image_media_id"
        mock_insta.publish_media.return_value = "Image posted successfully!"
        mock_insta.post_reel.return_value = "Failed to create reel container"
        mock_reel = mock_reel_cls.return_value
        mock_reel.prepare_tts_text.side_effect = lambda text: text
        mock_reel.create_reel.return_value = "mock_video.mp4"

        main.work()

        mock_insta.create_media_id.assert_called_once_with(
            "https://example.com/image_hd.jpg",
            "https://example.com/image.jpg",
            "Caption",
        )
        mock_insta.publish_media.assert_called_once_with(
            "image_media_id", "Caption"
        )

if __name__ == "__main__":
    unittest.main()

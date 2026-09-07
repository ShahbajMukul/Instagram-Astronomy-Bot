import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch
from reel_generator import ReelGenerator

class TestReelGenerator(unittest.TestCase):
    def test_prepare_tts_text_short(self):
        text = "This is a short cosmic sentence."
        result = ReelGenerator.prepare_tts_text(text)
        self.assertEqual(result, text)

    def test_prepare_tts_text_strips_hashtags_and_urls(self):
        text = "Check this out https://nasa.gov/apod amazing view! #space #universe"
        result = ReelGenerator.prepare_tts_text(text)
        self.assertNotIn("https://nasa.gov/apod", result)
        self.assertNotIn("#space", result)
        self.assertNotIn("#universe", result)
        self.assertIn("amazing view!", result)

    def test_prepare_tts_text_truncates_cleanly_at_sentence(self):
        long_text = "Stars are born in nebulae. " * 60 + "#astronomy"
        result = ReelGenerator.prepare_tts_text(long_text, max_chars=500)
        self.assertLessEqual(len(result), 500)
        self.assertTrue(result.endswith((".", "!", "?")))
        self.assertNotIn("#astronomy", result)

    @patch('reel_generator.Cartesia')
    @patch('reel_generator.os.getenv')
    def test_generate_speech(self, mock_getenv, mock_cartesia):
        mock_getenv.side_effect = lambda key, default=None: {
            "CARTESIA_KEY": "test-key",
            "CARTESIA_MODEL": "sonic-latest",
        }.get(key, default)
        mock_response = MagicMock()
        mock_response.write_to_file.side_effect = lambda path: open(
            path, "wb"
        ).write(b"cartesia wav")
        mock_client = mock_cartesia.return_value
        mock_client.voices.list.return_value = [
            MagicMock(id="voice-1"),
            MagicMock(id="voice-2"),
        ]
        mock_client.tts.generate.return_value = mock_response

        rg = ReelGenerator()
        audio_stream = rg.generate_speech("Hello universe! #stars")
        self.assertIsNotNone(audio_stream)
        self.assertEqual(audio_stream.read(), b"cartesia wav")
        mock_client.tts.generate.assert_called_once()
        self.assertIn(
            mock_client.tts.generate.call_args.kwargs["voice"],
            set(ReelGenerator.CARTESIA_VOICE_IDS),
        )

    @patch('reel_generator.os.listdir', return_value=[])
    @patch('reel_generator.os.path.isdir', return_value=True)
    def test_load_background_music_returns_none_when_folder_is_empty(
        self, mock_isdir, mock_listdir
    ):
        generator = ReelGenerator.__new__(ReelGenerator)
        generator.music_directory = "music"

        self.assertIsNone(generator._load_background_music(5))

if __name__ == "__main__":
    unittest.main()

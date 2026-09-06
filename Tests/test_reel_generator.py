import unittest
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

    def test_generate_speech(self):
        rg = ReelGenerator()
        audio_stream = rg.generate_speech("Hello universe! #stars")
        self.assertIsNotNone(audio_stream)
        audio_bytes = audio_stream.read()
        self.assertGreater(len(audio_bytes), 0)

if __name__ == "__main__":
    unittest.main()

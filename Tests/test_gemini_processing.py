import unittest
from unittest.mock import MagicMock
from gemini_processing import GeminiProcessing


class TestGeminiProcessingSanitization(unittest.TestCase):

    def test_sanitize_output_preserves_text_inside_code_fences(self):
        input_text = (
            "```\n"
            "This is paragraph one explaining the nebula.\n\n"
            "This is paragraph two explaining the star system.\n"
            "```"
        )
        expected = (
            "This is paragraph one explaining the nebula.\n\n"
            "This is paragraph two explaining the star system."
        )
        result = GeminiProcessing.sanitize_output(input_text)
        self.assertEqual(result, expected)

    def test_sanitize_output_preserves_paragraphs(self):
        input_text = (
            "Paragraph one.\n\n"
            "Paragraph two with **bold text** and *italic text*.\n\n"
            "Paragraph three."
        )
        expected = (
            "Paragraph one.\n\n"
            "Paragraph two with bold text and italic text.\n\n"
            "Paragraph three."
        )
        result = GeminiProcessing.sanitize_output(input_text)
        self.assertEqual(result, expected)

    def test_sanitize_output_strips_markdown_headers_and_links(self):
        input_text = (
            "### Cosmic Discovery\n\n"
            "Learn more at [NASA APOD](https://apod.nasa.gov)."
        )
        expected = (
            "Cosmic Discovery\n\n"
            "Learn more at NASA APOD."
        )
        result = GeminiProcessing.sanitize_output(input_text)
        self.assertEqual(result, expected)

    def test_sanitize_output_strips_html_tags(self):
        input_text = "<p>Welcome to <b>Space</b></p><br>Next line."
        expected = "Welcome to Space\n\nNext line."
        result = GeminiProcessing.sanitize_output(input_text)
        self.assertEqual(result, expected)

    def test_extract_response_text_ignores_thought_parts(self):
        candidate = MagicMock()
        thought_part = MagicMock()
        thought_part.thought = True
        thought_part.text = "Internal reasoning: I should summarize this."

        content_part = MagicMock()
        content_part.thought = False
        content_part.text = "Final caption output."

        candidate.content.parts = [thought_part, content_part]
        response = MagicMock()
        response.candidates = [candidate]

        result = GeminiProcessing.extract_response_text(response)
        self.assertEqual(result, "Final caption output.")


if __name__ == "__main__":
    unittest.main()

import html
import os
import re
from typing import Optional

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types


class GeminiProcessing:
    def __init__(self) -> None:
        load_dotenv()

        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.system_prompt = os.getenv(
            "GEMINI_SYSTEM_PROMPT",
            (
                "Rewrite the NASA Astronomy Picture of the Day explanation "
                "as an accurate, engaging Instagram caption. Explain scientific "
                "terms clearly. Do not invent facts. Do not use markdown."
            ),
        )
        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash",
        )

        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(api_key=self.gemini_api_key)

    @staticmethod
    def download_image(image_url: str) -> tuple[bytes, str]:
        """Download an image and return its bytes and MIME type."""
        response = requests.get(
            image_url,
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 Instagram-Astronomy-Bot/1.0"
                )
            },
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "image/jpeg")
        mime_type = content_type.split(";")[0].strip().lower()

        if not mime_type.startswith("image/"):
            raise ValueError(
                f"Expected an image from {image_url}, got {mime_type}"
            )

        return response.content, mime_type

    @staticmethod
    def extract_response_text(response) -> str:
        """
        Extract every textual part from a Gemini response.

        This avoids response.text failures when Gemini returns a response
        containing multiple parts, thought data, or other metadata.
        """
        text_parts: list[str] = []

        for candidate in response.candidates or []:
            content = getattr(candidate, "content", None)

            if not content:
                continue

            for part in content.parts or []:
                if getattr(part, "thought", False):
                    continue

                part_text = getattr(part, "text", None)

                if part_text:
                    text_parts.append(part_text)

        return "\n".join(text_parts).strip()

    @staticmethod
    def sanitize_output(text: str) -> str:
        """
        Normalize Gemini output for Instagram captions and TTS.

        This intentionally does not remove all non-ASCII characters because
        doing so corrupts names, scientific notation, and punctuation.
        """
        text = html.unescape(text)

        # Strip code fence markers without deleting text inside code blocks
        text = re.sub(r"```[a-zA-Z]*", "", text)

        # Convert HTML line breaks and paragraph tags to newlines
        text = re.sub(r"(?i)<br\s*/?>", "\n", text)
        text = re.sub(r"(?i)</p>", "\n\n", text)
        text = re.sub(r"(?i)<p[^>]*>", "", text)

        # Strip remaining HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Convert markdown links [text](url) -> text
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

        # Remove line-starting markdown headers (e.g. # Header or ## Header)
        text = re.sub(r"(?m)^#{1,6}\s*", "", text)

        # Remove bold/italic markers (*, _, `) while preserving text
        text = re.sub(r"[*_`]", "", text)

        # Remove bullet markers at start of lines (*, -, +)
        text = re.sub(r"(?m)^[ \t]*[*+\-]\s+", "", text)

        # Normalize line endings and whitespace per line while retaining paragraph breaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def generate_content(
        self,
        prompt: str,
        image_url: Optional[str] = None,
    ) -> str:
        fallback = self.sanitize_output(prompt)

        try:
            contents: list[types.Part | str] = [
                (
                    f"{self.system_prompt}\n\n"
                    "NASA's original APOD explanation:\n"
                    f"{prompt}"
                )
            ]

            if image_url:
                try:
                    image_bytes, mime_type = self.download_image(image_url)

                    contents.append(
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type=mime_type,
                        )
                    )
                except Exception as image_error:
                    # Caption generation can continue from NASA's explanation.
                    print(
                        "Warning: Gemini image input could not be loaded: "
                        f"{image_error}"
                    )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=1500,
                    response_mime_type="text/plain",
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold="BLOCK_MEDIUM_AND_ABOVE",
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold="BLOCK_MEDIUM_AND_ABOVE",
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_MEDIUM_AND_ABOVE",
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_MEDIUM_AND_ABOVE",
                        ),
                    ],
                ),
            )

            generated_text = self.extract_response_text(response)

            if not generated_text:
                print(
                    "Warning: Gemini returned no usable text. "
                    "Using NASA's original explanation."
                )
                return fallback

            print("Gemini generated the caption successfully.")
            return self.sanitize_output(generated_text)

        except Exception as error:
            print(
                "Error: Gemini caption generation failed. "
                f"Using NASA's original explanation. Details: {error}"
            )
            return fallback
import os
import google.generativeai as genai

from dotenv import load_dotenv

class GeminiProcessing:
    def __init__(self):
        load_dotenv()  
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.system_prompt = os.getenv("GEMINI_SYSTEM_PROMPT")
        
        genai.configure(api_key=self.gemini_api_key)
        
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                           generation_config=generation_config,
                                           safety_settings=safety_settings)

    def clean_text(self, text):
        # Escape special characters without over-escaping
        special_chars = {
            "\"": "\\\"",
            "'": "\'",  # Escape single quotes minimally
            "\\": "\\\\",  # Keep only one backslash escape
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;"
        }
        
        # Replace special characters
        for char, escaped_char in special_chars.items():
            text = text.replace(char, escaped_char)
        
        # Normalize spaces and keep original newlines
        cleaned_text = '\n'.join(' '.join(line.split()) for line in text.splitlines())
        return cleaned_text

    def generate_content(self, prompt, image_url):
        try:
            message = f"{self.system_prompt} {prompt}"
            response = self.model.generate_content(
                [message, image_url], 
                stream=True
            )
            
            if not response:
                print("Error: Empty response received from API")
                return prompt
                
            response.resolve()
            
            if hasattr(response, 'error') and response.error:
                print(f"Error: API returned error - {response.error}")
                return prompt
            
            print("Gemini read the content successfully and sent the response!")
            return self.clean_text(response.text)
            
        except Exception as e:
            print(f"Error: Failed to generate content - {str(e)}")
            return prompt

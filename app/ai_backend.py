"""
AI Backend for generating cover letters using OpenRouter or Gemini
"""
import os

from google import genai
from app.promtps import build_full_prompt


class AIBackend:
    def __init__(self):
        # self.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")
        # self.use_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))

        # Using Gemini API
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("No AI API key found in environment variables.")

        self.client = genai.Client(api_key=self.api_key)

        # Use gemini 2.0 flash
        self.model = "gemini-2.0-flash"

        # Generation config for consistent output
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

    def generate_cover_letters_with_tone(self, resume_text:str,job_description:str,tone:str = "professional") -> list[str]:
        """Generate 3 cover letters with specified tone using Gemini API"""

        prompt = build_full_prompt(tone, resume_text, job_description)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            # Extract text from response (Gemini returns object with .text)
            content = response.text.strip()
            variants = content.split("---VARIANT---")
            variants = [v.strip() for v in variants if v.strip()]

            if len(variants) < 3:
                import re
                variants = re.split(
                    r'\n\s*(?:Variant |Option |Letter )?[123][:.]?\s*\n',
                    content
                )
                variants = [v.strip() for v in variants if v.strip() and len(v) > 50]

            # Return at least one variant; ensure at most 3
            if variants and len(variants) >= 3:
                return variants[:3]
            elif variants:
                return variants
            else:
                return [content]
        except Exception as e:
            print(f"Error generating cover letters with Gemini: {e}")
            raise


# Singleton instance
ai_backend = AIBackend()

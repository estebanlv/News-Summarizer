# src/tools/summarizer.py
from google import genai
from typing import Optional

class Summarizer:
    """Gemini 2.5 Flash wrapper."""

    def __init__(self, api_key: str, model_name: str) -> None:
        # Create a Gen AI client (it will pick up your key here or from GOOGLE_API_KEY)
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def summarize(self, markdown: str, max_tokens: int = 256) -> str:
        prompt = (
            "Summarize the following news article in three crisp bullet points. "
            "Do not add commentary.\n\n"
            f"{markdown}"
        )
        # Call the Gen AI SDK
        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            # limit the response length
            max_output_tokens=max_tokens
        )
        return resp.text.strip()

"""
export GEMINI_API_KEY="YOUR_API_KEY"
uv pip install google-genai tqdm
uv run src/gemini3_pro.py
"""
import os
from lib.runner import run
from lib.llm_prompt import SYSTEM_PROMPT
from google import genai
from google.genai import types


def phonemize(sentence):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=sentence),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch()),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinkingConfig={
            "thinkingLevel": "HIGH",
        },
        tools=tools,
        system_instruction=[
            types.Part.from_text(text=SYSTEM_PROMPT),
        ],
    )

    result = ""
    for chunk in client.models.generate_content_stream(
        model="gemini-3-pro-preview",
        contents=contents,
        config=generate_content_config,
    ):
        result += chunk.text

    return result.strip()


if __name__ == "__main__":
    run(phonemize, "gemini3_pro")

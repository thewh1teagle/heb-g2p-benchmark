"""
Create API key at https://platform.openai.com
export OPENAI_API_KEY="YOUR_API_KEY"
uv pip install openai tqdm
uv run src/gpt52.py
"""
import os
from lib.runner import run
from lib.llm_prompt import SYSTEM_PROMPT
from openai import OpenAI


def phonemize(sentence):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.responses.create(
        model="gpt-5.2-chat-latest",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": SYSTEM_PROMPT
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": sentence
                    }
                ]
            }
        ],
        text={
            "format": {
                "type": "text"
            }
        },
        reasoning={},
        tools=[],
        temperature=1,
        max_output_tokens=2048,
        store=True,
        include=[
            "reasoning.encrypted_content",
            "web_search_call.action.sources"
        ]
    )

    return response.output_text.strip()


if __name__ == "__main__":
    run(phonemize, "gpt52")

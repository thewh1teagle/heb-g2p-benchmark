"""
Create API key at https://openrouter.ai/
export OPENROUTER_API_KEY="YOUR_API_KEY"
uv pip install openai tqdm
uv run src/gemini31_pro_high_openrouter.py
"""
import os
from openai import OpenAI
from lib.runner import run
from lib.llm_prompt import SYSTEM_PROMPT


def phonemize(sentence):
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    response = client.chat.completions.create(
        model="google/gemini-3.1-pro-preview",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": sentence},
        ],
        temperature=1,
        max_tokens=16384,
        extra_body={
            "reasoning": {
                "effort": "high",
                "exclude": True,
            },
        },
    )

    content = response.choices[0].message.content
    return (content or "").strip()


if __name__ == "__main__":
    run(phonemize, "gemini31_pro_high")

"""
export ANTHROPIC_API_KEY="YOUR_API_KEY"
uv pip install anthropic tqdm
uv run src/opus45.py
"""

import os
from lib.runner import run
from lib.llm_prompt import SYSTEM_PROMPT
import anthropic


def phonemize(sentence):
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )

    message = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=20000,
        temperature=1,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": [{"type": "text", "text": sentence}]}],
        thinking={"type": "enabled", "budget_tokens": 1024},
    )

    text = "".join(b.text for b in message.content if b.type == "text")
    return text.strip()


if __name__ == "__main__":
    run(phonemize, "opus45")

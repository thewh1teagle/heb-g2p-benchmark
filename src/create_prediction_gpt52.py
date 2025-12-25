"""
export OPENAI_API_KEY="YOUR_API_KEY"
uv pip install openai pandas tqdm
uv run src/create_prediction_gpt52.py
"""

import os
from openai import OpenAI
import pandas as pd
from tqdm import tqdm

SYSTEM_PROMPT = """You will receive Hebrew text. Convert it into IPA-like phonemes using ONLY the following symbols:

Vowels: a, e, i, o, u
Consonants: b, v, d, h, z, χ, t, j, k, l, m, n, s, f, p, ts, tʃ, w, ʔ, ɡ, ʁ, ʃ, ʒ, dʒ

Rules:
1. Every Hebrew word must include a stress mark.
2. Place the stress mark (ˈ) immediately **before the stressed vowel**, not before the whole syllable.
   Example: shalom → ʃalˈom
3. Keep punctuation exactly as in the input.
4. Output ONLY the phonemes (no explanations, no slashes).
5. Use ʔ for א / ע.
6. Don't add vowels or consonants that aren't written.

Examples:
שלום עולם → ʃalˈom ʔolˈam
מה קורה? → mˈa koʁˈe?
אתה יודע → ʔatˈa jodˈeʔa

Now wait for the text."""


def ask(prompt):
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
                        "text": prompt
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

    return response.output_text


if __name__ == "__main__":
    df = pd.read_csv("gt.tsv", sep='\t')
    results = []
    for index, row in tqdm(df.iterrows(), total=len(df)):
        sentence = row["Sentence"]
        phonemes = ask(sentence).strip()
        results.append({"Sentence": sentence, "Phonemes": phonemes})
        target_df = pd.DataFrame(results)
        target_df.to_csv("pred_gpt52.tsv", sep='\t', index=False)

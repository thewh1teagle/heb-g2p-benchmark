"""
uv pip install google-genai pandas tqdm
uv run src/gemma3.py
"""

import os
from google import genai
from google.genai import types
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

Now wait for the text.
"""


def ask(prompt):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-3-pro-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
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
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        result += chunk.text
    
    return result

if __name__ == "__main__":
    df = pd.read_csv("gt.csv")
    results = []
    for index, row in tqdm(df.iterrows(), total=len(df)):
        id = row["id"]
        transcript = row["transcript"]
        phonemes = ask(transcript).strip()
        results.append({"id": id, "phonemes": phonemes})
        target_df = pd.DataFrame(results)
        target_df.to_csv("pred_gemma3.csv", index=False)

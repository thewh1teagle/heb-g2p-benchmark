#!/usr/bin/env python3
"""
wget https://huggingface.co/thewh1teagle/gemma3-270m-heb-g2p/resolve/main/Modelfile
wget https://huggingface.co/thewh1teagle/gemma3-270m-heb-g2p/resolve/main/model-q8.gguf
ollama create gemma3-270m-heb-g2p -f ./Modelfile 

uv pip install ollama tqdm
uv run src/create_prediction_gemma3.py
"""

import ollama
import csv
from tqdm import tqdm

system_message = """You will receive Hebrew text. Convert it into IPA-like phonemes using ONLY the following symbols:

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

with open("gt.tsv", "r", encoding="utf-8") as f, open("pred_gemma3.tsv", "w", encoding="utf-8") as f_pred:
    reader = csv.DictReader(f, delimiter='\t')
    writer = csv.writer(f_pred, delimiter='\t')
    writer.writerow(["Sentence", "Phonemes"])

    for row in tqdm(reader):
        sentence = row["Sentence"]

        # Run inference with ollama
        response = ollama.chat(
            model="gemma3-270m-heb-g2p",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": sentence}
            ],
            options={
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 64,
                "num_predict": 150,
                "stop": ["<end_of_turn>", "</s>"]
            }
        )

        phonemes = response["message"]["content"].strip()
        writer.writerow([sentence, phonemes])

print("\nPredictions saved to pred_gemma3.tsv")
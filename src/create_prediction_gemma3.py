#!/usr/bin/env python3
"""
uv pip install ollama tqdm

uv run src/create_prediction_gemma3.py
"""

import ollama
import csv
from tqdm import tqdm

system_message = """Given the following Hebrew sentence, convert it to IPA phonemes.
Input Format: A Hebrew sentence.
Output Format: A string of IPA phonemes.
"""

with open("gt.tsv", "r", encoding="utf-8") as f, open("pred_gemma3.tsv", "w", encoding="utf-8") as f_pred:
    reader = csv.DictReader(f, delimiter='\t')
    writer = csv.writer(f_pred, delimiter='\t')
    writer.writerow(["Sentence", "Phonemes"])

    for row in tqdm(reader):
        sentence = row["Sentence"]

        # Run inference with ollama
        response = ollama.chat(
            model="gemma3-g2p",
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
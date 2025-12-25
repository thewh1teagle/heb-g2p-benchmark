"""
uv pip install phonemizer-fork espeakng-loader     

uv run src/create_prediction_espeak-ng.py
"""
import csv
from tqdm import tqdm

from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer import phonemize
import espeakng_loader

EspeakWrapper.set_library(espeakng_loader.get_library_path())
EspeakWrapper.set_data_path(espeakng_loader.get_data_path())

# Example usage:
if __name__ == "__main__":
    with open("gt.tsv", "r", encoding="utf-8") as f, open("pred_espeak-ng.tsv", "w", encoding="utf-8") as f_pred:
        reader = csv.reader(f, delimiter='\t')
        next(reader) # skip header
        writer = csv.writer(f_pred, delimiter='\t')
        writer.writerow(["Sentence", "Phonemes"])
        for row in tqdm(reader):
            sentence = row[0]
            phonemes = phonemize(sentence, language="he")
            writer.writerow([sentence, phonemes])
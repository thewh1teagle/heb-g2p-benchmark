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
    with open("gt.csv", "r") as f, open("pred_espeak-ng.csv", "w") as f_pred:
        reader = csv.reader(f)
        next(reader) # skip header
        writer = csv.writer(f_pred)
        writer.writerow(["id", "phonemes"])
        for row in tqdm(reader):
            id = row[0]
            transcript = row[1]
            phonemes = phonemize(transcript, language="he")
            writer.writerow([id, phonemes])
"""
uv pip install pygoruut     

uv run src/create_prediction_goruut.py
"""
from pygoruut.pygoruut import Pygoruut
import csv
from tqdm import tqdm

pygoruut = None

def phonemize(sentence: str) -> str:
    global pygoruut
    if pygoruut is None:
        pygoruut = Pygoruut(version='v0.6.3')

    return str(pygoruut.phonemize(language="Hebrew3", sentence=sentence))

# Example usage:
if __name__ == "__main__":
    with open("gt.tsv", "r", encoding="utf-8") as f, open("pred_goruut.tsv", "w", encoding="utf-8") as f_pred:
        reader = csv.reader(f, delimiter='\t')
        next(reader) # skip header
        writer = csv.writer(f_pred, delimiter='\t')
        writer.writerow(["Sentence", "Phonemes"])
        for row in tqdm(reader):
            sentence = row[0]
            phonemes = phonemize(sentence)
            writer.writerow([sentence, phonemes])
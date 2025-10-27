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
    with open("gt.csv", "r") as f, open("pred_goruut.csv", "w") as f_pred:
        reader = csv.reader(f)
        next(reader) # skip header
        writer = csv.writer(f_pred)
        writer.writerow(["id", "phonemes"])
        for row in tqdm(reader):
            id = row[0]
            transcript = row[1]
            phonemes = phonemize(transcript)
            writer.writerow([id, phonemes])
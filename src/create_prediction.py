"""
wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
uv pip install phonikud phonikud-onnx tqdm

uv run src/create_prediction.py
"""


from phonikud_onnx import Phonikud
from phonikud import phonemize
from tqdm import tqdm
import csv

model = Phonikud("./phonikud-1.0.int8.onnx")

with open("gt.csv", "r") as f, open("pred.csv", "w") as f_pred:
    reader = csv.reader(f)
    next(reader) # skip header
    writer = csv.writer(f_pred)
    writer.writerow(["id", "phonemes"])
    for row in tqdm(reader):
        id = row[0]
        transcript = row[1]
        vocalized = model.add_diacritics(transcript)
        phonemes = phonemize(vocalized)
        writer.writerow([id, phonemes])


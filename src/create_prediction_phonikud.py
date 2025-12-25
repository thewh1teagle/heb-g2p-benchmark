"""
wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
uv pip install phonikud phonikud-onnx tqdm

uv run src/create_prediction_phonikud.py
"""


from phonikud_onnx import Phonikud
from phonikud import phonemize
from tqdm import tqdm
import csv

model = Phonikud("./phonikud-1.0.int8.onnx")

with open("gt.tsv", "r", encoding="utf-8") as f, open("pred_phonikud.tsv", "w", encoding="utf-8") as f_pred:
    reader = csv.reader(f, delimiter='\t')
    next(reader) # skip header
    writer = csv.writer(f_pred, delimiter='\t')
    writer.writerow(["Sentence", "Phonemes"])
    for row in tqdm(reader):
        sentence = row[0]
        vocalized = model.add_diacritics(sentence)
        phonemes = phonemize(vocalized)
        writer.writerow([sentence, phonemes])


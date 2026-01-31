import csv
import os
from tqdm import tqdm

DELIMITER = '\t'


def count_existing_rows(path):
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return max(0, sum(1 for _ in f) - 1)


def run(phonemize_fn, output_name):
    pred_path = f"pred_{output_name}.tsv"
    skip = count_existing_rows(pred_path)
    mode = "a" if skip > 0 else "w"

    with open("gt.tsv", "r", encoding="utf-8") as f, \
         open(pred_path, mode, encoding="utf-8") as f_pred:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        next(reader)
        writer = csv.writer(f_pred, delimiter=DELIMITER)

        if mode == "w":
            writer.writerow(["Sentence", "Phonemes"])

        for _ in range(skip):
            next(reader)

        if skip > 0:
            print(f"Resuming from row {skip + 1}")

        for row in tqdm(reader):
            sentence = row["Sentence"]
            phonemes = phonemize_fn(sentence)
            writer.writerow([sentence, phonemes])
            f_pred.flush()
